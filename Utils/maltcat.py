#!/usr/bin/env python
import sys
import zipfile
import json
import xml.etree.ElementTree as ET
import os
from pathlib import Path

def parse_entity_definition(entity_content):
    """Parse entity XML to extract field definitions"""
    root = ET.fromstring(entity_content)
    entity_id = root.get('id')
    display_name = root.get('displayName')
    
    fields = {}
    properties = root.find('Properties')
    if properties is not None:
        fields_elem = properties.find('Fields')
        if fields_elem is not None:
            for field in fields_elem.findall('Field'):
                field_name = field.get('name')
                field_type = field.get('type')
                field_desc = field.get('description', '')
                display_name_attr = field.get('displayName', field_name)
                
                fields[field_name] = {
                    'type': field_type,
                    'description': field_desc,
                    'display_name': display_name_attr
                }
    
    return {
        'id': entity_id,
        'display_name': display_name,
        'fields': fields
    }


def extract_lucene_data(lucene_dir):
    """Extract data from Lucene index directory using Java LuceneReader"""
    import subprocess
    
    if not os.path.exists(lucene_dir):
        return []
    
    # Try to use our compiled Java LuceneReader with Lucene 6.6.6
    java_home = "/opt/homebrew/Cellar/openjdk@21/21.0.7/libexec/openjdk.jdk/Contents/Home"
    lucene_cp = "/Users/brain/work/gits/Maltego2Arango/lucene-6.6.6/core/lucene-core-6.6.6.jar:/Users/brain/work/gits/Maltego2Arango/lucene-6.6.6/backward-codecs/lucene-backward-codecs-6.6.6.jar"
    
    # Check if LuceneReader.class exists
    reader_class = "/Users/brain/work/gits/Maltego2Arango/LuceneReader.class"
    if os.path.exists(reader_class):
        try:
            env = os.environ.copy()
            env['JAVA_HOME'] = java_home
            
            result = subprocess.run([
                'java', '-cp', f'{lucene_cp}:.', 
                'LuceneReader', lucene_dir
            ], capture_output=True, text=True, env=env, 
            cwd='/Users/brain/work/gits/Maltego2Arango')
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'output': result.stdout,
                    'method': 'Java LuceneReader'
                }
            else:
                return {
                    'status': 'error', 
                    'error': result.stderr,
                    'method': 'Java LuceneReader'
                }
        except Exception as e:
            return {
                'status': 'exception',
                'error': str(e),
                'method': 'Java LuceneReader'
            }
    
    # Fallback: just list files
    lucene_files = []
    if os.path.exists(lucene_dir):
        for file in os.listdir(lucene_dir):
            lucene_files.append(file)
    
    return {
        'files': lucene_files,
        'status': 'file_list_only',
        'method': 'Directory listing'
    }


def read_maltego_file(mtgl_path):
    """Read and parse Maltego .mtgl file"""
    entity_definitions = {}
    
    with zipfile.ZipFile(mtgl_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        
        # First pass: extract entity definitions
        for filename in file_list:
            if filename.endswith('.entity'):
                with zip_ref.open(filename) as file:
                    content = file.read()
                    try:
                        entity_def = parse_entity_definition(content)
                        entity_definitions[entity_def['id']] = entity_def
                        print(f"Entity: {entity_def['id']} - {entity_def['display_name']}")
                        for field_name, field_info in entity_def['fields'].items():
                            print(f"  Field: {field_name} ({field_info['type']}) - {field_info['display_name']}")
                    except Exception as e:
                        print(f"Error parsing {filename}: {e}")
    
    return entity_definitions


def process_extracted_graph(graph_path, entity_definitions):
    """Process extracted graph data from filesystem"""
    data_entities_path = os.path.join(graph_path, "DataEntities")
    structure_entities_path = os.path.join(graph_path, "StructureEntities")


    print(f"\nAnalyzing Lucene indexes:")
    print(f"DataEntities: {extract_lucene_data(data_entities_path)}")
    print(f"StructureEntities: {extract_lucene_data(structure_entities_path)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mtgl_path = sys.argv[1]
    else:
        mtgl_path = "/Users/brain/work/gits/Maltego2Arango/Sample/Maltego.mtgl"
    
    print("=== Parsing Maltego File ===")
    entity_defs = read_maltego_file(mtgl_path)
    
    print("\n=== Processing Extracted Graph Data ===")
    graph_path = "/Users/brain/work/gits/Maltego2Arango/Sample/Graphs/Graph1"
    process_extracted_graph(graph_path, entity_defs)