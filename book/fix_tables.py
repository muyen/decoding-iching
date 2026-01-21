#!/usr/bin/env python3
"""
Convert markdown tables to code block format for better PDF rendering.
"""
import re
import os
from pathlib import Path

def parse_markdown_table(table_text):
    """Parse a markdown table into rows and columns."""
    lines = [l.strip() for l in table_text.strip().split('\n') if l.strip()]

    # Filter out separator lines (|---|---|)
    data_lines = []
    for line in lines:
        # Skip separator lines
        if re.match(r'^\|[-:\s|]+\|$', line):
            continue
        # Parse cells
        cells = [c.strip() for c in line.split('|')]
        # Remove empty first/last cells from |cell|cell| format
        cells = [c for c in cells if c]
        if cells:
            data_lines.append(cells)

    return data_lines

def format_as_code_block(rows):
    """Format table rows as a nicely aligned code block."""
    if not rows:
        return ""

    # Calculate max width for each column
    num_cols = max(len(row) for row in rows)
    col_widths = []

    for col_idx in range(num_cols):
        max_width = 0
        for row in rows:
            if col_idx < len(row):
                # Account for Chinese characters (2 width) vs ASCII (1 width)
                text = row[col_idx]
                width = sum(2 if ord(c) > 127 else 1 for c in text)
                max_width = max(max_width, width)
        col_widths.append(max_width + 2)  # Add padding

    # Format rows
    output_lines = []

    for row_idx, row in enumerate(rows):
        formatted_cells = []
        for col_idx, cell in enumerate(row):
            # Calculate padding needed
            cell_width = sum(2 if ord(c) > 127 else 1 for c in cell)
            padding = col_widths[col_idx] - cell_width
            formatted_cells.append(cell + ' ' * padding)

        output_lines.append(''.join(formatted_cells).rstrip())

        # Add separator after header
        if row_idx == 0:
            separator = '─' * (sum(col_widths))
            output_lines.append(separator)

    return '```\n' + '\n'.join(output_lines) + '\n```'

def convert_tables_in_file(filepath):
    """Convert all markdown tables in a file to code blocks."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match markdown tables
    # A table starts with | and has at least a header and separator
    table_pattern = re.compile(
        r'(\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)+)',
        re.MULTILINE
    )

    def replace_table(match):
        table_text = match.group(1)
        rows = parse_markdown_table(table_text)
        if rows:
            return format_as_code_block(rows)
        return table_text

    new_content = table_pattern.sub(replace_table, content)

    # Only write if changed
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    book_dir = Path('/Users/arsenelee/github/iching/book')

    # Process chapters
    chapters_dir = book_dir / 'chapters'
    for md_file in chapters_dir.glob('*.md'):
        if convert_tables_in_file(md_file):
            print(f"✓ Converted tables in: {md_file.name}")

    # Process front matter
    front_dir = book_dir / 'front_matter'
    for md_file in front_dir.glob('*.md'):
        if convert_tables_in_file(md_file):
            print(f"✓ Converted tables in: {md_file.name}")

    # Process back matter
    back_dir = book_dir / 'back_matter'
    for md_file in back_dir.glob('*.md'):
        if convert_tables_in_file(md_file):
            print(f"✓ Converted tables in: {md_file.name}")

    print("\nDone! All tables converted to code block format.")

if __name__ == '__main__':
    main()
