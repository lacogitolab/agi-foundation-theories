#!/usr/bin/env python3
"""
Script to scan folders and extract PDF metadata
"""
import os
import json
from pathlib import Path
from collections import defaultdict

try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfFileReader as PdfReader
    except ImportError:
        print("Error: pypdf or PyPDF2 library not found. Install with: pip install pypdf")
        exit(1)


def extract_pdf_metadata(pdf_path):
    """Extract metadata from a PDF file"""
    metadata = {
        'Name': '',
        'Author': '',
        'Date': '',
        'Publisher': ''
    }
    
    def to_string(value):
        """Convert value to string, handling ByteStringObject and other types"""
        if value is None:
            return ''
        try:
            return str(value)
        except:
            return ''
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            
            # Get metadata
            if reader.metadata:
                meta = reader.metadata
                
                # Extract Title/Name
                if '/Title' in meta:
                    metadata['Name'] = to_string(meta['/Title'])
                elif hasattr(meta, 'title'):
                    metadata['Name'] = to_string(meta.title)
                
                # Extract Author
                if '/Author' in meta:
                    metadata['Author'] = to_string(meta['/Author'])
                elif hasattr(meta, 'author'):
                    metadata['Author'] = to_string(meta.author)
                
                # Extract Date
                if '/CreationDate' in meta:
                    metadata['Date'] = to_string(meta['/CreationDate'])
                elif '/ModDate' in meta:
                    metadata['Date'] = to_string(meta['/ModDate'])
                elif hasattr(meta, 'creation_date'):
                    metadata['Date'] = to_string(meta.creation_date)
                
                # Extract Publisher
                if '/Producer' in meta:
                    metadata['Publisher'] = to_string(meta['/Producer'])
                elif hasattr(meta, 'producer'):
                    metadata['Publisher'] = to_string(meta.producer)
                elif '/Creator' in meta:
                    metadata['Publisher'] = to_string(meta['/Creator'])
            
            # If no metadata found, use filename as name
            if not metadata['Name']:
                metadata['Name'] = os.path.basename(pdf_path)
                
    except Exception as e:
        print(f"Error reading {pdf_path}: {str(e)}")
        metadata['Name'] = os.path.basename(pdf_path)
    
    return metadata


def scan_directory(root_dir):
    """Scan directory structure and extract PDF metadata"""
    structure = defaultdict(lambda: defaultdict(list))
    
    root_path = Path(root_dir)
    
    # Walk through all directories
    for item in root_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            folder_name = item.name
            
            # Scan subdirectories and files
            for subitem in item.rglob('*'):
                if subitem.is_file() and subitem.suffix.lower() == '.pdf':
                    # Get relative path components
                    rel_path = subitem.relative_to(root_path)
                    path_parts = rel_path.parts
                    
                    if len(path_parts) >= 2:
                        # Main folder
                        main_folder = path_parts[0]
                        
                        # Subfolder (if exists)
                        if len(path_parts) > 2:
                            subfolder = '/'.join(path_parts[1:-1])
                        else:
                            subfolder = '.'  # Root of main folder
                        
                        # Extract metadata
                        metadata = extract_pdf_metadata(subitem)
                        metadata['FileName'] = subitem.name
                        metadata['FullPath'] = str(subitem)
                        
                        structure[main_folder][subfolder].append(metadata)
    
    return structure


def format_output(structure):
    """Format the structure as a readable list"""
    output = []
    
    for folder_name in sorted(structure.keys()):
        output.append(f"\n{'='*80}")
        output.append(f"FOLDER: {folder_name}")
        output.append(f"{'='*80}")
        
        for subfolder in sorted(structure[folder_name].keys()):
            if subfolder == '.':
                output.append(f"\n  SUBFOLDER: (root)")
            else:
                output.append(f"\n  SUBFOLDER: {subfolder}")
            
            output.append(f"  {'-'*76}")
            
            for file_info in sorted(structure[folder_name][subfolder], key=lambda x: x['FileName']):
                output.append(f"    File: {file_info['FileName']}")
                output.append(f"      Name: {file_info['Name']}")
                output.append(f"      Author: {file_info['Author']}")
                output.append(f"      Date: {file_info['Date']}")
                output.append(f"      Publisher: {file_info['Publisher']}")
                output.append("")
    
    return '\n'.join(output)


def main():
    root_dir = "/Users/chenxm/My Drive/agi-foundation-theories"
    
    print("Scanning directories and extracting PDF metadata...")
    print("This may take a while for large collections...\n")
    
    structure = scan_directory(root_dir)
    
    # Also save as JSON for programmatic access
    json_file = os.path.join(root_dir, "pdf_metadata_list.json")
    # Convert defaultdict to regular dict for JSON serialization
    json_structure = {k: {sk: sv for sk, sv in v.items()} for k, v in structure.items()}
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_structure, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nOutput saved to:")
    print(f"  - {json_file}")


if __name__ == "__main__":
    main()

