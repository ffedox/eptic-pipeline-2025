import numpy as np
from bertalign import model
from bertalign.corelib import *
import pandas as pd
from bertalign.utils import *
import csv

import torch  # Assuming PyTorch is already imported as per your code

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

class Bertalign:
    def __init__(self,
                 src,
                 tgt,
                 src_lang,  # Add these parameters
                 tgt_lang,
                 max_align=5,
                 top_k=3,
                 win=5,
                 skip=-0.1,
                 margin=True,
                 len_penalty=True,
                 is_split=True,
               ):
        
        self.max_align = max_align
        self.top_k = top_k
        self.win = win
        self.skip = skip
        self.margin = margin
        self.len_penalty = len_penalty
        
        src = clean_text(src)
        tgt = clean_text(tgt)
        
        if is_split:
            src_sents = src.splitlines()
            #print(src_sents)
            tgt_sents = tgt.splitlines()
            #print(tgt_sents)
        else:
            src_sents = split_sents(src, src_lang)
            tgt_sents = split_sents(tgt, tgt_lang)
 
        src_num = len(src_sents)
        tgt_num = len(tgt_sents)
        
        src_lang = LANG.ISO[src_lang]
        tgt_lang = LANG.ISO[tgt_lang]
        
        src_vecs, src_lens = model.transform(src_sents, max_align - 1)
        tgt_vecs, tgt_lens = model.transform(tgt_sents, max_align - 1)

        char_ratio = np.sum(src_lens[0,]) / np.sum(tgt_lens[0,])

        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.src_sents = src_sents
        self.tgt_sents = tgt_sents
        self.src_num = src_num
        self.tgt_num = tgt_num
        self.src_lens = src_lens
        self.tgt_lens = tgt_lens
        self.char_ratio = char_ratio
        self.src_vecs = src_vecs
        self.tgt_vecs = tgt_vecs
        
    def align_sents(self):
        D, I = find_top_k_sents(self.src_vecs[0,:], self.tgt_vecs[0,:], k=self.top_k)
        first_alignment_types = get_alignment_types(2) # 0-1, 1-0, 1-1
        first_w, first_path = find_first_search_path(self.src_num, self.tgt_num)
        first_pointers = first_pass_align(self.src_num, self.tgt_num, first_w, first_path, first_alignment_types, D, I)
        first_alignment = first_back_track(self.src_num, self.tgt_num, first_pointers, first_path, first_alignment_types)
        
        second_alignment_types = get_alignment_types(self.max_align)
        second_w, second_path = find_second_search_path(first_alignment, self.win, self.src_num, self.tgt_num)
        second_pointers = second_pass_align(self.src_vecs, self.tgt_vecs, self.src_lens, self.tgt_lens,
                                            second_w, second_path, second_alignment_types,
                                            self.char_ratio, self.skip, margin=self.margin, len_penalty=self.len_penalty)
        second_alignment = second_back_track(self.src_num, self.tgt_num, second_pointers, second_path, second_alignment_types)
        
        self.result = second_alignment

    def save_aligned_sentences_to_files(self, src_file_path, tgt_file_path):
        """
        Saves the aligned sentences into two separate text files.

        :param src_file_path: Path to save the source sentences.
        :param tgt_file_path: Path to save the target sentences.
        """
        with open(src_file_path, 'w', encoding='utf-8') as src_file, open(tgt_file_path, 'w', encoding='utf-8') as tgt_file:
            for bead in self.result:
                # Extracting the aligned sentences
                src_line = self._get_line(bead[0], self.src_sents)
                print(src_line)
                tgt_line = self._get_line(bead[1], self.tgt_sents)
                print(tgt_line)
                
                # Writing the sentences to their respective files
                if src_line:  # Ensure the line is not empty
                    src_file.write(f"<s>{src_line}</s>\n")
                if tgt_line:  # Ensure the line is not empty
                    tgt_file.write(f"<s>{tgt_line}</s>\n")

    def get_sentences_as_dict(self):
        data = {
            'Source ID': [],
            'Source Sentence': [],
            'Target ID': [],
            'Target Sentence': []
        }
        max_len = max(len(self.src_sents), len(self.tgt_sents))
        for i in range(max_len):
            # Handle Source Sentences
            if i < len(self.src_sents):
                src_sentence = self.src_sents[i]
                src_id_tag = f"{self.src_lang}:{i + 1}"
                data['Source ID'].append(src_id_tag)
                data['Source Sentence'].append(src_sentence)
            else:
                data['Source ID'].append('')
                data['Source Sentence'].append('')

            # Handle Target Sentences
            if i < len(self.tgt_sents):
                tgt_sentence = self.tgt_sents[i]
                tgt_id_tag = f"{self.tgt_lang}:{i + 1}"
                data['Target ID'].append(tgt_id_tag)
                data['Target Sentence'].append(tgt_sentence)
            else:
                data['Target ID'].append('')
                data['Target Sentence'].append('')

        return data


    def save_alignment_indices_to_csv(self, csv_file_path):
        """
        Saves the alignment indices to a CSV file. Each row contains the index of a source sentence
        and the corresponding aligned target sentence indices.
        """
        # Open the CSV file for writing
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write the header
            writer.writerow(['Source Indices', 'Target Indices'])
            
            # Iterate over the alignment results and write the indices
            for bead in self.result:
                src_index = ','.join(str(idx + 1) for idx in bead[0]) if bead[0] else ''
                tgt_index = ','.join(str(idx + 1) for idx in bead[1]) if bead[1] else ''
                writer.writerow([src_index, tgt_index])


    def get_result(self):
        aligned_text_pairs = []
        for bead in self.result:
            src_line = self._get_line(bead[0], self.src_sents)
            tgt_line = self._get_line(bead[1], self.tgt_sents)
            aligned_text_pairs.append((src_line, tgt_line))
        return self.result, aligned_text_pairs
    
    def print_sents(self):
        for bead in self.result:
            src_line = self._get_line(bead[0], self.src_sents)
            tgt_line = self._get_line(bead[1], self.tgt_sents)
            print(f"Source: {src_line}\nTarget: {tgt_line}\n")

    @staticmethod
    def _get_line(bead, lines):
        line = ''
        if len(bead) > 0:
            line = ' '.join(lines[bead[0]:bead[-1]+1])
        return line