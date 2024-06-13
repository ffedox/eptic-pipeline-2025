# EPTIC update pipeline

Pipeline to 

1. Export vert files from an .xlsx dump of the db 
2. Align everything from scratch

All the rest (metadata, subtitles) is assumed to be there but subtitles can be missing

**Requirements:**

a folder with all text ids by language (ids)
a folder with all alignment pairs by language pair (alignments)

cd bertalign

Step 1

align_texts_new_pipeline.py

in folder "alignments" creates _aligned.xlsx files

Step 3

bertalign_to_intertext_pipeline2.py

additional fixes resulting in "_formatted.xlsx" files

Step 4

postprocess_and_output_xmls_pipeline.py

in folder "alignments" creates _updated.xlsx files with "alignment" column containing the alignment in xml format

Step 5 

texts_to_pretgd_pipeline3.py

prepare pretgd files

Step 6?

Export alignments?

