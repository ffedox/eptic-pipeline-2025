import pandas as pd
import xml.etree.ElementTree as ET
import glob
import os

# Function to prettify XML content
def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed_string = rough_string.decode('utf-8').replace('><', '>\n<')
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    return xml_declaration + reparsed_string

# Function to convert CSV to Intertext XML and save it
def convert_csv_to_intertext_and_save(csv_file_path):
    df = pd.read_csv(csv_file_path)
    df['intertext_xml'] = df['alignment_output'].apply(lambda x: convert_to_intertext(eval(x)))
    df['processed_xml'] = df.apply(process_xml_content, axis=1)
    formatted_file_path = csv_file_path.replace('.csv', '_formatted.xlsx')
    df[['first_id', 'second_id', 'processed_xml']].to_excel(formatted_file_path, index=False)
    print(f"Formatted XML saved to {formatted_file_path}")
    return formatted_file_path

# Function to update the original Excel files with formatted XML content
def update_original_files_with_formatted_content(formatted_file_path):
    original_file_path = formatted_file_path.replace('alignment_results_', '').replace('_formatted', '')
    if not os.path.exists(original_file_path):
        print(f"Original file does not exist for: {formatted_file_path}")
        return
    formatted_df = pd.read_excel(formatted_file_path)
    original_df = pd.read_excel(original_file_path)
    update_dict = formatted_df.set_index(['first_id', 'second_id'])['processed_xml'].to_dict()
    
    def update_row(row):
        if pd.isna(row['alignment']):
            return update_dict.get((row['first_id'], row['second_id']), row['alignment'])
        else:
            return row['alignment']
    
    original_df['alignment'] = original_df.apply(update_row, axis=1)

    # Check for any NA in 'alignment' after the update
    if original_df['alignment'].isna().any():
        print(f"Warning: After updating, '{original_file_path}' contains rows with NA in the 'alignment' column.")

    updated_file_path = original_file_path.replace('.xlsx', '_updated.xlsx')
    original_df.to_excel(updated_file_path, index=False)
    print(f"Updated file saved to {updated_file_path}")

# Helpers for converting alignments to XML
def convert_to_intertext(alignments):
    root = ET.Element('linkGrp', attrib={'toDoc': 'placeholder_toDoc.xml', 'fromDoc': 'placeholder_fromDoc.xml'})
    for left_side, right_side in alignments:
        link = ET.SubElement(root, 'link', attrib={
            'xtargets': ';'.join([' '.join(map(str, side)) for side in [left_side, right_side]]),
            'type': f"{len(left_side)}-{len(right_side)}",
            'status': 'manual'
        })
    return prettify(root)

def process_xml_content(row):
    try:
        intertext_element = ET.fromstring(row['intertext_xml'])
        for link in intertext_element.findall('.//link'):
            xtargets = link.get('xtargets')
            left, right = xtargets.split(';')
            left_nums = ' '.join([f"{row['first_id']}:{int(num)+1}" for num in left.split() if num.isdigit()])
            right_nums = ' '.join([f"{row['second_id']}:{int(num)+1}" for num in right.split() if num.isdigit()])
            link.set('xtargets', f"{left_nums};{right_nums}")
        return prettify(intertext_element)
    except ET.ParseError:
        return ""

# Main process
if __name__ == '__main__':
    folder_path = '/home/afedotova/eptic-pipeline/scripts/alignments'
    for csv_file in glob.glob(os.path.join(folder_path, '*.csv')):
        formatted_file_path = convert_csv_to_intertext_and_save(csv_file)
        update_original_files_with_formatted_content(formatted_file_path)
