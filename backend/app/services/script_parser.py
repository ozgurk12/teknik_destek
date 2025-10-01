import re
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class VideoScriptParser:
    """Parser for extracting structured data from generated video scripts"""

    @staticmethod
    def parse_script(script_text: str) -> Dict:
        """
        Parse the video script text and extract structured information

        Returns a dictionary with:
        - title: Video title
        - subject: Subject/ders
        - age_group: Target age group
        - duration: Estimated duration
        - character: Character name (e.g., Atlas)
        - sections: List of sections with their content
        """
        try:
            # First try to parse as JSON
            try:
                # Clean the text - remove any markdown code blocks if present
                cleaned_text = script_text.strip()
                if cleaned_text.startswith('```json'):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.startswith('```'):
                    cleaned_text = cleaned_text[3:]
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3]

                parsed_json = json.loads(cleaned_text.strip())

                # Ensure the JSON has the expected structure
                if isinstance(parsed_json, dict) and 'sections' in parsed_json:
                    parsed_json['raw_text'] = script_text
                    return parsed_json
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, fall back to text parsing
                pass

            result = {
                "title": "",
                "subject": "",
                "age_group": "",
                "duration": "",
                "character": "Atlas",
                "sections": [],
                "raw_text": script_text
            }

            lines = script_text.split('\n')
            current_section = None
            current_subsection = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Extract title (Video Başlığı)
                if '**[Video Başlığı]**' in line or 'Video Başlığı:' in line:
                    next_line_idx = lines.index(line) + 1
                    if next_line_idx < len(lines):
                        result['title'] = lines[next_line_idx].strip().replace('*', '')

                # Extract subject (Ders)
                if '**Ders:**' in line or 'Ders:' in line:
                    result['subject'] = line.replace('**Ders:**', '').replace('Ders:', '').strip().replace('*', '')

                # Extract age group (Hedef Yaş Grubu)
                if '**Hedef Yaş Grubu:**' in line or 'Hedef Yaş Grubu:' in line:
                    result['age_group'] = line.replace('**Hedef Yaş Grubu:**', '').replace('Hedef Yaş Grubu:', '').strip().replace('*', '')

                # Extract duration (Video Süresi)
                if '**Video Süresi:**' in line or 'Video Süresi:' in line:
                    result['duration'] = line.replace('**Video Süresi:**', '').replace('Video Süresi:', '').strip().replace('*', '')

                # Extract character
                if '**Karakter:**' in line or 'Karakter:' in line:
                    result['character'] = line.replace('**Karakter:**', '').replace('Karakter:', '').strip().replace('*', '')

                # Parse sections (BÖLÜM)
                section_match = re.match(r'(?:\*\*)?(?:###\s*)?(\d+)\.\s*BÖLÜM:?\s*(.*?)(?:\*\*)?', line, re.IGNORECASE)
                if section_match:
                    section_num = section_match.group(1)
                    section_title = section_match.group(2).strip().replace('*', '').replace('[', '').replace(']', '')

                    current_section = {
                        "section_number": int(section_num),
                        "title": section_title,
                        "background": "",
                        "character": "",
                        "text": "",
                        "subsections": []
                    }
                    result['sections'].append(current_section)
                    current_subsection = None

                # Parse subsections within a section
                elif current_section:
                    # Background (Arka Plan)
                    if re.search(r'(?:\*\*)?1\.\s*Arka Plan.*?(?:\*\*)?', line, re.IGNORECASE):
                        current_subsection = 'background'
                    # Character description
                    elif re.search(r'(?:\*\*)?2\.\s*Seslendiren Karakter.*?(?:\*\*)?', line, re.IGNORECASE):
                        current_subsection = 'character'
                    # Main text (Metin)
                    elif re.search(r'(?:\*\*)?3\.\s*Metin.*?(?:\*\*)?', line, re.IGNORECASE):
                        current_subsection = 'text'
                    # Collect content for current subsection
                    elif current_subsection and not re.match(r'^\d+\.', line):
                        if current_subsection == 'background':
                            current_section['background'] += line + '\n'
                        elif current_subsection == 'character':
                            current_section['character'] += line + '\n'
                        elif current_subsection == 'text':
                            current_section['text'] += line + '\n'

            # Clean up the sections
            for section in result['sections']:
                section['background'] = section['background'].strip()
                section['character'] = section['character'].strip()
                section['text'] = section['text'].strip()

            # Extract visual cues from text (things in parentheses)
            for section in result['sections']:
                visual_cues = re.findall(r'\*\*\((.*?)\)\*\*', section['text'])
                section['visual_cues'] = visual_cues

            return result

        except Exception as e:
            logger.error(f"Error parsing script: {str(e)}")
            return {
                "title": "",
                "subject": "",
                "age_group": "",
                "duration": "",
                "character": "Atlas",
                "sections": [],
                "raw_text": script_text,
                "parse_error": str(e)
            }

    @staticmethod
    def format_for_display(parsed_script: Dict) -> str:
        """Format parsed script for display"""
        output = []

        if parsed_script.get('title'):
            output.append(f"📽️ **{parsed_script['title']}**\n")

        if parsed_script.get('subject'):
            output.append(f"📚 **Ders:** {parsed_script['subject']}")

        if parsed_script.get('age_group'):
            output.append(f"👶 **Yaş Grubu:** {parsed_script['age_group']}")

        if parsed_script.get('duration'):
            output.append(f"⏱️ **Süre:** {parsed_script['duration']}")

        if parsed_script.get('character'):
            output.append(f"🎭 **Karakter:** {parsed_script['character']}")

        output.append("\n---\n")

        for section in parsed_script.get('sections', []):
            output.append(f"\n### {section['section_number']}. BÖLÜM: {section['title']}\n")

            if section['background']:
                output.append(f"**🎨 Arka Plan:**\n{section['background']}\n")

            if section['character']:
                output.append(f"**🗣️ Karakter:**\n{section['character']}\n")

            if section['text']:
                output.append(f"**📝 Metin:**\n{section['text']}\n")

            if section.get('visual_cues'):
                output.append(f"**👁️ Görsel İpuçları:** {', '.join(section['visual_cues'])}\n")

        return '\n'.join(output)