import pandas as pd
import re
import glob
import os
from xml.dom.minidom import parseString
from xml.etree import ElementTree as ET

def process_alignment(alignment):
    """Clean and format alignment XML content."""
    alignment = re.sub(r'<(?!.*?\/>).*?>', '', alignment)
    alignment = alignment.replace('"', "'")
    alignment = alignment.replace('manual', "man")
    alignment = re.sub(r"\s*'/>\s*", "'/>", alignment)
    return alignment

def rearrange_link_attributes(xml_string):
    """Rearranges attributes in <link> tags to have 'type', 'xtargets', and then 'status'."""
    tree = ET.ElementTree(ET.fromstring(xml_string))
    root = tree.getroot()
    for link in root.findall('.//link'):
        attributes = link.attrib
        # Extract attributes in specific order and remove them from the element
        ordered_attributes = {k: attributes.pop(k) for k in ['type', 'xtargets', 'status'] if k in attributes}
        # Clear all attributes and set them back in the desired order
        link.attrib.clear()
        link.attrib.update(ordered_attributes)
    # Convert back to string ensuring all quotes are single
    return ET.tostring(root, encoding='unicode').replace(' />', '/>').replace('"', "'")

def prettify_and_refine_xml(xml_string):
    """Refines XML string without adding any indentation or spaces, and ensures single quotes are used."""
    xml_string = rearrange_link_attributes(xml_string)  # Rearrange attributes in link tags
    # Remove indentations and line breaks between tags
    xml_string = re.sub(r'>\s*<', '><', xml_string)
    # Ensure tags start at the beginning of each line
    xml_string = re.sub(r'(<)', r'\n\1', xml_string).strip()
    # Ensure all quotes in attributes are single quotes
    xml_string = xml_string.replace('"', "'")
    return xml_string

def process_files(folder_path):
    """Process each updated Excel file to generate and refine XML content."""
    for file_path in glob.glob(os.path.join(folder_path, '*_updated.xlsx')):
        print(f"Processing file: {file_path}")
        df = pd.read_excel(file_path)

        # Apply processing to each alignment entry
        df['processed'] = df['alignment'].astype(str).apply(process_alignment)

        # Construct XML content without initial declaration for further processing
        xml_content = "<linkGrp toDoc='placeholder_toDoc.xml' fromDoc='placeholder_fromDoc.xml'>" + ''.join(df['processed'].tolist()) + "</linkGrp>"

        # Further refine XML content
        refined_xml = prettify_and_refine_xml(xml_content)

        # Explicitly add the XML declaration to the refined XML content
        xml_declaration = "<?xml version='1.0' encoding='utf-8'?>\n"
        final_xml_content = xml_declaration + refined_xml

        # Define output XML file path with the new naming scheme
        base_file_name = os.path.basename(file_path)
        new_file_name = base_file_name.replace('_updated.xlsx', '') + '.xml'
        output_xml_path = os.path.join(os.path.dirname(file_path), new_file_name)
        
        # Write the final XML content, including the declaration, to file
        with open(output_xml_path, 'w', encoding='utf-8') as file:
            file.write(final_xml_content)
        
        print(f"Refined XML saved to: {output_xml_path}")



if __name__ == '__main__':
    folder_path = '/home/afedotova/bertalign/trash/lang_combinations'
    process_files(folder_path)
