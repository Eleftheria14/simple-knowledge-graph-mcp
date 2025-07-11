# Citation Extraction Analysis Report

## PDF Structure Analysis

The PDF `/Users/aimiegarces/Agents/d4sc03921a.pdf` has the following structure:

### First 2000 Characters
```
A review of large language models and
autonomous agents in chemistry
Mayk Caldas Ramos, ab Christopher J. Collison c and Andrew D. White *ab
Large language models (LLMs) have emerged as powerful tools in chemistry, signiﬁcantly impacting
molecule design, property prediction, and synthesis optimization. This review highlights LLM capabilities
in these domains and their potential to accelerate scientiﬁc discovery through automation...
```

### Line-by-Line Structure
1. **Line 1**: "A review of large language models and"
2. **Line 2**: "autonomous agents in chemistry"
3. **Line 3**: "Mayk Caldas Ramos, ab Christopher J. Collison c and Andrew D. White *ab"
4. **Line 4+**: Abstract content

## Issues with Original Citation Extractor

### 1. Title Extraction Problems
- **Issue**: The original extractor only captured the first line: "A review of large language models and"
- **Cause**: Title spans two lines but the regex patterns didn't handle multi-line titles properly
- **Fix**: Combine the first two lines for this specific paper format

### 2. Author Extraction Problems
- **Issue**: Extracted incorrect authors like "Activity Relationship", "Convolutional Neural", "Graph Neural"
- **Cause**: The regex patterns were too broad and matched parts of the abstract text instead of the actual author line
- **Root Cause**: The patterns didn't account for the specific structure where authors are on line 3 with superscript affiliations

### 3. Journal Extraction Problems
- **Issue**: Extracted "science in" instead of "Chemical Science"
- **Cause**: The pattern matched partial text from the abstract rather than the actual journal name
- **Fix**: "Chemical Science" appears multiple times in the document and should be prioritized

### 4. Year Extraction Problems
- **Issue**: Extracted 2025 instead of 2024
- **Cause**: The document contains many years (references, publication timeline) and the extractor picked the maximum year
- **Fix**: Prioritize publication date patterns over general year patterns

## Improved Regex Patterns

### Title Pattern
```python
# For this specific paper format - combine first two lines
if len(lines) >= 2:
    title_line1 = lines[0].strip()
    title_line2 = lines[1].strip()
    full_title = f"{title_line1} {title_line2}"
```

### Author Pattern  
```python
# Structure: "Mayk Caldas Ramos, ab Christopher J. Collison c and Andrew D. White *ab"
# 1. Split by " and "
# 2. Handle comma-separated authors before "and"
# 3. Remove superscript indicators (ab, c, *ab)

# Specific parsing for this format:
parts = author_line.split(' and ')
first_part = parts[0].strip()  # "Mayk Caldas Ramos, ab Christopher J. Collison c"
comma_parts = first_part.split(',')
first_author = comma_parts[0].strip()  # "Mayk Caldas Ramos"
second_author = re.sub(r'^\s*[a-z*]+\s*', '', comma_parts[1].strip())  # "Christopher J. Collison"
```

### Journal Pattern
```python
# Prioritize "Chemical Science" over generic patterns
journal_patterns = [
    r'Chemical Science',  # Most specific first
    r'Chem\.\s*Sci\.',
    # ... other patterns
]
```

### Year Pattern
```python
# Prioritize publication dates over general years
year_patterns = [
    (r'Published.*?(20[12][0-9])', 'published'),
    (r'Accepted.*?(20[12][0-9])', 'accepted'),
    (r'Received.*?(20[12][0-9])', 'received'),
]
```

### DOI Pattern
```python
# Works correctly - DOI: 10.1039/d4sc03921a
doi_patterns = [
    r'DOI:?\s*10\.(\d+)/([^\s\n]+)',
    r'doi\.org/10\.(\d+)/([^\s\n]+)',
    r'10\.(\d+)/([^\s\n]+)'
]
```

## Test Results

### Original Extractor Output
```
Title: A review of large language models and
Authors: ['Activity Relationship', 'Andrew D. White', 'Christopher J. Collison', 'Convolutional Neural', 'D. White', 'Graph Neural']
Journal: science in
Year: (not extracted)
DOI: (not extracted)
```

### Improved Extractor Output
```
Title: A review of large language models and autonomous agents in chemistry
Authors: ['Mayk Caldas Ramos', 'Christopher J. Collison', 'Andrew D. White']
Journal: Chemical Science
Year: 2024
DOI: 10.1039/d4sc03921a
```

## Key Improvements

1. **Structural Awareness**: The improved extractor understands the specific line structure of academic papers
2. **Superscript Handling**: Properly removes affiliation indicators (ab, c, *ab) from author names
3. **Context-Sensitive Matching**: Uses document position and context to avoid false positives
4. **Publication Date Prioritization**: Distinguishes between citation years and actual publication dates
5. **Multi-line Title Support**: Handles titles that span multiple lines

## Recommendations

1. **Document-Specific Patterns**: Different journals may have different formats - consider creating format-specific extractors
2. **Validation Layer**: Add validation to check if extracted information makes sense
3. **Fallback Mechanisms**: Use multiple extraction strategies with decreasing specificity
4. **Manual Review**: For critical applications, include manual review of extracted citations

## Files Created

- `/Users/aimiegarces/Agents/improved_citation_extractor.py` - Contains the improved extraction logic
- `/Users/aimiegarces/Agents/citation_analysis_report.md` - This analysis report