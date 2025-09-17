# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains Turkish preschool educational curriculum data based on the Maarif Model (Maarif Model Okul Öncesi). The main data file is a CSV containing learning outcomes and competencies for preschool education.

## Data Structure

The CSV file `Maarif Model Okul Öncesi Kazanımlar.csv` contains:
- **7044 lines** of educational curriculum data
- **UTF-8 encoding with BOM**
- **Semicolon-delimited** format
- Mixed line endings (CRLF and LF)

### Column Structure
- Yaş (Age): Age groups (e.g., 36-48 months, 48-60 months)
- Ders (Subject): Subject areas (TÜRKÇE, MATEMATİK, etc.)
- Alan Becerileri (Field Skills): Main skill areas
- Bütünleşik Beceriler (Integrated Skills): Cross-functional skills
- Süreç Bileşenleri (Process Components): Learning process elements
- Öğrenme Çıktıları (Learning Outcomes): Primary learning objectives
- Alt Öğrenme Çıktıları (Sub-Learning Outcomes): Detailed learning objectives

## Working with the Data

### Reading the CSV
When processing this file:
- Use semicolon (`;`) as the delimiter
- Handle UTF-8 BOM properly
- Be aware of multiline fields containing newlines within quoted text
- Some fields contain structured text with prefixes like "TAB1.1.SB1" indicating hierarchical categorization

### Data Processing Commands

```bash
# View column headers
head -1 "Maarif Model Okul Öncesi Kazanımlar.csv"

# Count records by age group
cut -d';' -f1 "Maarif Model Okul Öncesi Kazanımlar.csv" | sort | uniq -c

# Extract specific subject data (e.g., TÜRKÇE)
grep "TÜRKÇE" "Maarif Model Okul Öncesi Kazanımlar.csv"
```

## Key Considerations

1. **Language**: All content is in Turkish. When working with this data, preserve Turkish characters and text formatting.

2. **Educational Context**: This is curriculum data for preschool education (okul öncesi) following the Maarif educational model used in Turkish education system.

3. **Data Complexity**: Fields contain hierarchical educational taxonomies with specific coding systems (e.g., TADB, TAB1.1, etc.) that should be preserved when processing.

4. **Age Groups**: Data is organized by developmental age ranges typical for preschool education (36-48 months, 48-60 months, etc.)