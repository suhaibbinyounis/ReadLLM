#!/usr/bin/env python3
"""
Fix YAML frontmatter in Hugo markdown files.

Issues fixed:
1. List items (tags, categories) need proper 2-space indentation
2. Remove unnecessary single quotes from date values
3. Multi-line descriptions/titles need to be joined into a single line
4. Titles with single quotes need to use double quotes
5. Dates in the future are set to current time
"""

import re
from datetime import datetime, timezone
from pathlib import Path


def fix_frontmatter(content: str) -> str:
    """Fix the YAML frontmatter in a markdown file."""
    
    if not content.startswith("---"):
        return content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content
    
    frontmatter = parts[1]
    body = parts[2]
    
    lines = frontmatter.split("\n")
    fixed_lines = []
    i = 0
    
    # Current time for fixing future dates
    now = datetime.now(timezone.utc)
    now_str = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"
    
    while i < len(lines):
        line = lines[i]
        
        # Handle date - fix if in the future
        date_match = re.match(r"^date:\s*'?([^']+)'?$", line)
        if date_match:
            date_value = date_match.group(1).strip()
            try:
                # Parse the date
                parsed_date = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                if parsed_date > now:
                    # Date is in the future, use current time
                    fixed_lines.append(f"date: {now_str}")
                else:
                    fixed_lines.append(f"date: {date_value}")
            except:
                fixed_lines.append(f"date: {now_str}")
            i += 1
            continue
        
        # Handle title with single quotes - convert to double quotes
        title_match = re.match(r"^title:\s*'(.+)'$", line)
        if title_match:
            title_value = title_match.group(1)
            fixed_lines.append(f'title: "{title_value}"')
            i += 1
            continue
        
        # Handle multi-line fields (description, title without quotes)
        field_match = re.match(r'^(title|description):\s*(.*)$', line)
        if field_match:
            field_name = field_match.group(1)
            field_value = field_match.group(2).strip()
            
            # Check if next lines are continuations (start with 2+ spaces, not a list item)
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if next_line.startswith("  ") and not next_line.strip().startswith("-"):
                    field_value += " " + next_line.strip()
                    j += 1
                else:
                    break
            
            fixed_lines.append(f"{field_name}: {field_value}")
            i = j
            continue
        
        # Handle list keys (tags, categories)
        if re.match(r'^(tags|categories):\s*$', line):
            fixed_lines.append(line)
            i += 1
            # Process list items - add indentation if missing
            while i < len(lines):
                list_line = lines[i]
                if list_line.startswith("- "):
                    fixed_lines.append("  " + list_line)
                    i += 1
                elif list_line.startswith("  - "):
                    fixed_lines.append(list_line)  # Already indented
                    i += 1
                else:
                    break
            continue
        
        # Pass through other lines
        fixed_lines.append(line)
        i += 1
    
    fixed_frontmatter = "\n".join(fixed_lines)
    return f"---{fixed_frontmatter}---{body}"


def main():
    """Process all markdown files in the current directory."""
    script_dir = Path(__file__).parent
    md_files = list(script_dir.glob("*.md"))
    
    fixed_count = 0
    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        fixed_content = fix_frontmatter(content)
        
        if content != fixed_content:
            md_file.write_text(fixed_content, encoding="utf-8")
            print(f"✓ Fixed: {md_file.name}")
            fixed_count += 1
        else:
            print(f"  Skipped (already valid): {md_file.name}")
    
    print(f"\n{'='*50}")
    print(f"Done! Fixed {fixed_count} of {len(md_files)} files.")


if __name__ == "__main__":
    main()
