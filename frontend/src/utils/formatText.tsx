import React from 'react';
import { Typography, Box } from '@mui/material';

export const formatMarkdownText = (text: string) => {
  if (!text) return null;
  
  // Split text into lines
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  
  lines.forEach((line, index) => {
    // Check for headers
    if (line.startsWith('### ')) {
      elements.push(
        <Typography key={index} variant="h6" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
          {line.substring(4)}
        </Typography>
      );
    } else if (line.startsWith('## ')) {
      elements.push(
        <Typography key={index} variant="h5" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
          {line.substring(3)}
        </Typography>
      );
    } else if (line.startsWith('# ')) {
      elements.push(
        <Typography key={index} variant="h4" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
          {line.substring(2)}
        </Typography>
      );
    } 
    // Check for bullet points
    else if (line.trim().startsWith('• ') || line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      const bulletChar = line.trim().substring(0, 1);
      const content = line.trim().substring(2);
      elements.push(
        <Box key={index} sx={{ display: 'flex', mb: 0.5 }}>
          <Typography component="span" sx={{ mr: 1 }}>•</Typography>
          <Typography component="span" sx={{ flex: 1 }}>
            {formatInlineMarkdown(content)}
          </Typography>
        </Box>
      );
    }
    // Check for numbered lists
    else if (/^\d+\.\s/.test(line.trim())) {
      const match = line.trim().match(/^(\d+)\.\s(.*)$/);
      if (match) {
        elements.push(
          <Box key={index} sx={{ display: 'flex', mb: 0.5 }}>
            <Typography component="span" sx={{ mr: 1, minWidth: '24px' }}>{match[1]}.</Typography>
            <Typography component="span" sx={{ flex: 1 }}>
              {formatInlineMarkdown(match[2])}
            </Typography>
          </Box>
        );
      }
    }
    // Empty lines
    else if (line.trim() === '') {
      elements.push(<Box key={index} sx={{ height: '0.5em' }} />);
    }
    // Regular text
    else {
      elements.push(
        <Typography key={index} component="div" sx={{ mb: 0.5 }}>
          {formatInlineMarkdown(line)}
        </Typography>
      );
    }
  });
  
  return <>{elements}</>;
};

// Helper function to format inline markdown (bold, italic, etc.)
const formatInlineMarkdown = (text: string): React.ReactNode => {
  // Handle bold text
  const boldRegex = /\*\*(.*?)\*\*/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match;
  
  while ((match = boldRegex.exec(text)) !== null) {
    // Add text before the match
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    // Add bold text
    parts.push(
      <strong key={match.index}>{match[1]}</strong>
    );
    lastIndex = match.index + match[0].length;
  }
  
  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }
  
  return parts.length > 0 ? parts : text;
};

export default formatMarkdownText;