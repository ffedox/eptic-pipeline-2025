import pandas as pd
from xml.etree import ElementTree as ET
from bertalign import Bertalign
import os
import glob
import csv

def process_xml_sentences(xml_str):
    if pd.isnull(xml_str):
        return ""
    try:
        root = ET.fromstring(xml_str)
        sentences = [s.text for s in root.findall('.//s') if s.text is not None]
        return '\n'.join(sentences)
    except ET.ParseError:
        return ""

def extract_lang_codes(filename):
    base_name = os.path.basename(filename)
    parts = base_name.split("__")
    src_lang = parts[0][:2]  # First two characters of the filename
    tgt_lang = parts[1][:2]  # First two characters after "__"
    return src_lang, tgt_lang

def align_sents(src_text, tgt_text, src_lang, tgt_lang, writer):
    aligner = Bertalign(src_text, tgt_text, src_lang=src_lang, tgt_lang=tgt_lang)
    aligner.align_sents()
    # Instead of saving directly to a CSV, pass the writer object
    aligner.save_aligned_sentences_to_csv(writer)

def process_files(texts_data_path, alignment_files_folder):
    texts_data = pd.read_excel(texts_data_path, dtype={'texts.id': str})
    texts_data['processed_text'] = texts_data['texts.sentence_split_text'].apply(process_xml_sentences)
    id_to_processed_text = pd.Series(texts_data.processed_text.values, index=texts_data['texts.id']).to_dict()

    for alignment_file_path in glob.glob(os.path.join(alignment_files_folder, '*.xlsx')):
        print(f"Processing alignment file: {alignment_file_path}")
        excel_output_path = alignment_file_path.replace('.xlsx', '_aligned.xlsx')
        all_data = []

        missing_alignments_data = pd.read_excel(alignment_file_path, dtype={'first_id': str, 'second_id': str})
        for _, row in missing_alignments_data.iterrows():
            src_text = id_to_processed_text.get(row['first_id'], "")
            tgt_text = id_to_processed_text.get(row['second_id'], "")
            if src_text and tgt_text:
                src_lang, tgt_lang = extract_lang_codes(alignment_file_path)
                aligner = Bertalign(src_text, tgt_text, src_lang=src_lang, tgt_lang=tgt_lang)
                aligner.align_sents()
                sentences_data = aligner.get_sentences_as_dict()
                sentences_data['first_id'] = row['first_id']
                sentences_data['second_id'] = row['second_id']
                all_data.append(sentences_data)

        if all_data:
            df = pd.concat([pd.DataFrame(data) for data in all_data], ignore_index=True)
            df.to_excel(excel_output_path, index=False)
            print(f"Data saved to {excel_output_path}.")
        else:
            print(f"No valid data to process in {alignment_file_path}.")

def main():
    texts_data_path = '/home/afedotova/eptic-pipeline/eptic-pipeline/database/texts.xlsx'
    alignment_files_folder = '/home/afedotova/eptic-pipeline/eptic-pipeline/scripts/alignments'
    process_files(texts_data_path, alignment_files_folder)

if __name__ == '__main__':
    main()
