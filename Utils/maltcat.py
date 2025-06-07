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
    """Extract data from Lucene index directory using Java subprocess"""
    import subprocess
    
    if not os.path.exists(lucene_dir):
        return []
    
    java_code = f'''
import org.apache.lucene.index.*;
import org.apache.lucene.store.*;
import org.apache.lucene.document.*;
import java.nio.file.Paths;
import java.util.*;

public class LuceneExtractor {{
    public static void main(String[] args) {{
        try {{
            Directory dir = FSDirectory.open(Paths.get("{lucene_dir}"));
            if (DirectoryReader.indexExists(dir)) {{
                DirectoryReader reader = DirectoryReader.open(dir);
                System.out.println("Documents: " + reader.numDocs());
                
                for (int i = 0; i < Math.min(reader.numDocs(), 10); i++) {{
                    Document doc = reader.document(i);
                    System.out.println("Document " + i + ":");
                    for (IndexableField field : doc.getFields()) {{
                        System.out.println("  " + field.name() + ": " + field.stringValue());
                    }}
                }}
                reader.close();
            }} else {{
                System.out.println("No valid Lucene index found");
            }}
            dir.close();
        }} catch (Exception e) {{
            System.out.println("Error: " + e.getMessage());
        }}
    }}
}}
'''
    
    # For now, just list files and return basic info
    lucene_files = []
    if os.path.exists(lucene_dir):
        for file in os.listdir(lucene_dir):
            lucene_files.append(file)
    
    return {
        'files': lucene_files,
        'java_extraction': 'Available with full Java classpath setup'
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