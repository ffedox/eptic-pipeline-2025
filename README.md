# eptic-pipeline

Developer-side code for the construction of EPTIC.

# Installation

Installing [Bertalign](https://github.com/bfsujason/bertalign) and [WhisperX](https://github.com/m-bain/whisperX) in 5 steps:

```
git clone https://github.com/ffedox/eptic-pipeline3/

conda env create -f environment.yml

conda activate pipeline-eptic2

pip install torch==2.0.0+cu117 torchaudio==2.0.0+cu117 -f https://download.pytorch.org/whl/torch_stable.html

pip install git+https://github.com/m-bain/whisperx.git
```

Additionally, you may want to [install ffmpeg](https://ffmpeg.org/download.html) for manipulating video files and extracting audio tracks.

# EPTIC Workflow

![Eptic Workflow](eptic_workflow.jpg)

# Guided Example

TBD
