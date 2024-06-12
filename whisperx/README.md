# eptic-pipeline

https://colab.research.google.com/drive/1HH7yV-_lYufEeQEPiDCGYaOG3M1eDJyc#scrollTo=OIW4k8_nRXt9

## Pipeline steps

Clone this repository 

![Eptic Workflow](eptic_workflow.jpg)

### 1. Video and text extraction

Can be done on https://multimedia.europarl.europa.eu/en/webstreaming?view=day&d=2011-02-16 (as of June 2024)

Alternatively, it could be previously be done on https://www.europarl.europa.eu/plenary/en/debates-video.html. As of June 2024 this method wasn't functioning anymore, with the Multimedia Center option being the only one available.

Then we need to separate the audio tracks we're interested in (with FFMPEG)

ffmpeg -i /yourpath/eptic-pipeline/data/videos/0001.wmv -> list audio tracks with ffmpeg

if wav

ffmpeg -i /yourpath/eptic-pipeline/data/videos/0001.wmv -map 0:3 -c:a libmp3lame -q:a 2 italian_track.mp3
 -> getting italian
 
ffmpeg -i /yourpath/eptic-pipeline/data/videos/0001.wmv -map 0:0 -c:a libmp3lame -q:a 2 english_track.mp3
 -> getting english

 if mp4

ffmpeg -i /yourpath/eptic-pipeline/data/videos/0001.wmv -map 0:0 -c:a aac -b:a 128k english_track.mp4

ffmpeg -i /yourpath/eptic-pipeline/data/videos/0001.wmv -map 0:3 -c:a aac -b:a 128k italian_track.mp4


### 2. Transcription

Now that we have an audio per track we can transcribe

Recommended software: [**WhisperX**](https://github.com/m-bain/whisperX). Performs transcription and provides timestamps. Installation instructions in the linked page. Review sentence segmentation.

whisperx english_track.mp4

whisperx italian_track.mp4

### 3. Sentence alignment

Recommended software: [**Bertalign**]([https://github.com/m-bain/whisperX](https://github.com/bfsujason/bertalign)).

When using Bertalign on previously segmented sentences, set ```is_split``` to ```True``` in ```aligner.py```. Review sentence alignments.

### 4. Metadata extraction

TBD



### 5. Manual metadata selection and review

Insert ```speech_type``` information and review transcription.


## Guided installation and practical example

### Installation steps

Setting up env

conda create --name eptictools python=3.10

conda activate eptictools

Installing whisperX

conda install pytorch==2.0.0 torchaudio==2.0.0 pytorch-cuda=11.8 -c pytorch -c nvidia

pip install git+https://github.com/m-bain/whisperx.git

 git clone https://github.com/m-bain/whisperX.git

cd whisperX

pip install -e .

Installing Bertalign

git clone https://github.com/bfsujason/bertalign

cd bertalign

pip install -r requirements.txt

from now on activate eptictools when moving to installation directory to open up the installed software

### Practical example




