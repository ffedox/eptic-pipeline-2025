# eptic-pipeline

Developer-side code and documentation for the construction of EPTIC.

# Installation

Installing [Bertalign](https://github.com/bfsujason/bertalign) and [WhisperX](https://github.com/m-bain/whisperX) in 5 steps:

```
git clone https://github.com/ffedox/eptic-pipeline/
cd eptic-pipeline
conda env create -f environment.yml
conda activate eptic-pipeline
```

When reusing this repository activate the conda environment again with conda activate pipeline-eptic2.

Additionally, you may want to [install ffmpeg](https://ffmpeg.org/download.html) for manipulating video files and extracting audio tracks.

# EPTIC Workflow

1. Video and text extraction
2. Transcription
3. Sentence alignment
4. Manual metadata selection and review

# Guided Example

### 1. Video and text extraction

Can be done on https://multimedia.europarl.europa.eu/en/webstreaming?view=day&d=2011-02-16 (as of June 2024)

Alternatively, it could be previously be done on https://www.europarl.europa.eu/plenary/en/debates-video.html. As of June 2024 this method wasn't functioning anymore, with the Multimedia Center option being the only one available.

Then we need to separate the audio tracks we're interested in (with ffmpeg it would be:)

Listing audio tracks:

ffmpeg -i /yourpath/eptic-pipeline/data/videos/0001.wmv -> list audio tracks with ffmpeg

If .wav:

ffmpeg -i /yourpath/eptic-pipeline/data/videos/0001.wmv -map 0:3 -c:a libmp3lame -q:a 2 italian_track.mp3
 -> getting italian
 
ffmpeg -i /yourpath/eptic-pipeline/data/videos/0001.wmv -map 0:0 -c:a libmp3lame -q:a 2 english_track.mp3
 -> getting english

If .mp4:

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


### 4. Manual metadata selection and review

Insert ```speech_type``` and other metadata and review transcription.
