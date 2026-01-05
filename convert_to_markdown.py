#!/usr/bin/env python3
"""
Convert PDF metadata JSON to markdown format
"""
import json
import os
import re
from urllib.parse import quote
from pathlib import Path


def extract_year_from_date(date_str):
    """Extract year from PDF date string (format: D:YYYYMMDD...)"""
    if not date_str:
        return ''
    
    # Try to extract year from PDF date format: D:YYYYMMDD...
    match = re.search(r'D:(\d{4})', date_str)
    if match:
        return match.group(1)
    
    # Try to extract year from other formats
    match = re.search(r'(\d{4})', date_str)
    if match:
        year = match.group(1)
        # Validate year is reasonable (1900-2100)
        if 1900 <= int(year) <= 2100:
            return year
    
    return ''


def format_author(author_str):
    """Format author string"""
    if not author_str or author_str.strip() == '':
        return ''
    return author_str.strip()


def format_publisher(publisher_str):
    """Format publisher string, removing common technical terms"""
    if not publisher_str or publisher_str.strip() == '':
        return ''
    
    publisher = publisher_str.strip()
    
    # Remove common technical PDF producer names
    technical_terms = [
        'Acrobat Distiller', 'pdfTeX', 'GPL Ghostscript', 'ESP Ghostscript',
        'AFPL Ghostscript', 'Quartz PDFContext', 'iText', 'dvips', 'dvipdfm',
        'Mac OS X', 'Windows', 'Microsoft', 'Adobe', 'Skia/PDF', 'Google Docs',
        'PowerPoint', 'Word', 'Excel', 'LibreOffice', 'Ghostscript'
    ]
    
    # If publisher is just a technical term, return empty
    for term in technical_terms:
        if term.lower() in publisher.lower():
            # Check if it's mostly technical
            if len(publisher) < 50:  # Short technical strings
                return ''
    
    return publisher


def get_folder_emoji(folder_name):
    """Get emoji for folder based on name"""
    emoji_map = {
        'algorithm-design': '🔧',
        'category-theory': '📐',
        'computability-logic': '🧮',
        'computability-theory': '⚙️',
        'control-theory': '🎛️',
        'cryptography': '🔐',
        'data-science': '📊',
        'deep-learning': '🧠',
        'engineering-agi': '🤖',
        'fuzzy-graph-theory': '🧠',
        'game-theory': '🎮',
        'graph-theory': '🕸️',
        'information-theory': '📡',
        'lambda-calculus': 'λ',
        'machine-learning': '🤖',
        'mathematical-logic': '📚',
        'neuroscience': '🧠',
        'quantum-computing': '⚛️',
        'set-theory': '📦',
        'spatiotempral-statistics': '📈',
        'type-theory': '🔤',
        'uncertainty-theory': '❓'
    }
    return emoji_map.get(folder_name, '📄')


def format_folder_name(folder_name):
    """Format folder name for display"""
    return folder_name.replace('-', ' ').title()


def create_markdown_entry(file_info, folder_name, subfolder):
    """Create a markdown entry for a single file"""
    name = file_info.get('Name', '')
    author = format_author(file_info.get('Author', ''))
    date = file_info.get('Date', '')
    publisher = format_publisher(file_info.get('Publisher', ''))
    file_name = file_info.get('FileName', '')
    file_path = file_info.get('FullPath', file_info.get('FileName', ''))
    
    # Extract year
    year = extract_year_from_date(date)
    
    # Build relative path for link
    if file_path.startswith('/'):
        # Get relative path from root
        root_dir = "/Users/chenxm/My Drive/agi-foundation-theories"
        try:
            rel_path = os.path.relpath(file_path, root_dir)
        except:
            # Fallback: construct path from folder and filename
            if subfolder == '.':
                rel_path = f"{folder_name}/{file_name}"
            else:
                rel_path = f"{folder_name}/{subfolder}/{file_name}"
    else:
        rel_path = file_path
    
    # Determine title - use Name if it's meaningful, otherwise use filename
    # A name is meaningful if it's different from the filename and not just a technical identifier
    if name and name != file_name:
        # Check if name looks like a real title (not just a technical identifier)
        if len(name) > 5 and not name.lower().endswith('.pdf'):
            title = name
        else:
            # Clean up filename to use as title
            title = file_name.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
    else:
        # Clean up filename to use as title
        title = file_name.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
    
    # Build the entry
    parts = [title]
    
    # Author
    if author:
        parts.append(f" — {author}")
    
    # Year
    if year:
        parts.append(f", {year}")
    
    # Publisher
    if publisher:
        parts.append(f", {publisher}")
    
    entry = ''.join(parts)
    
    # Create markdown link - use quote only once, properly
    link_path = quote(rel_path, safe='/')
    link_text = rel_path
    
    return f"- {entry}  \n  [`{link_text}`]({link_path})"


def convert_to_markdown(json_file, output_file):
    """Convert JSON metadata to markdown format"""
    print(f"Reading {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    markdown_lines = []
    
    # Sort folders
    for folder_name in sorted(data.keys()):
        emoji = get_folder_emoji(folder_name)
        folder_display = format_folder_name(folder_name)
        
        markdown_lines.append(f"## {emoji} {folder_display}")
        markdown_lines.append("")
        
        folder_data = data[folder_name]
        
        # Sort subfolders
        for subfolder in sorted(folder_data.keys()):
            files = folder_data[subfolder]
            
            # Sort files by name
            files_sorted = sorted(files, key=lambda x: x.get('FileName', ''))
            
            for file_info in files_sorted:
                entry = create_markdown_entry(file_info, folder_name, subfolder)
                markdown_lines.append(entry)
                markdown_lines.append("")
        
        markdown_lines.append("")
    
    # Write to file
    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_lines))
    
    print(f"Done! Created {output_file}")


def main():
    root_dir = "/Users/chenxm/My Drive/agi-foundation-theories"
    json_file = os.path.join(root_dir, "pdf_metadata_list.json")
    output_file = os.path.join(root_dir, "pdf_metadata_list.md")
    
    convert_to_markdown(json_file, output_file)


if __name__ == "__main__":
    main()

