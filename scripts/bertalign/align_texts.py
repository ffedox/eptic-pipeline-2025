import pandas as pd
from bertalign import Bertalign

# Load the Excel file
file_path = '/home/afedotova/eptic-pipeline-2/eptic-pipeline/database/texts.xlsx'
df = pd.read_excel(file_path)

# Group the texts by event_id
grouped = df.groupby('texts.event_id')

# Function to align texts and return alignments
def align_texts(src, tgt):
    aligner = Bertalign(src, tgt)
    aligner.align_sents()
    # Extract and format alignments
    alignments = []
    for bead in aligner.result:
        src_line = aligner._get_line(bead[0], aligner.src_sents)
        tgt_line = aligner._get_line(bead[1], aligner.tgt_sents)
        alignments.append(f"{src_line} --> {tgt_line}")
    return alignments

# Prepare the list to store results
results = []

# Iterate through each group and align texts
for event_id, group in grouped:
    texts = group['texts.plain_text'].tolist()
    ids = group['texts.id'].tolist()
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            src = texts[i]
            tgt = texts[j]
            alignments = align_texts(src, tgt)
            results.append([ids[i], ids[j], alignments])

# Create a DataFrame for the results
results_df = pd.DataFrame(results, columns=['src_id', 'tgt_id', 'alignments'])

# Save the results to a CSV file
output_file_path = '/home/afedotova/eptic-pipeline-2/eptic-pipeline/scripts/bertalign/alignments.csv'
results_df.to_csv(output_file_path, index=False)

print(f"Alignments saved to {output_file_path}")
