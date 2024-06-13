# Guided Example

This is a guided example illustrating the suggested workflow for EPTIC.

### 1. Video and text extraction

Can be done on https://multimedia.europarl.europa.eu/en/webstreaming?view=day&d=2011-02-16 (as of June 2024)

Alternatively, it could be previously be done on https://www.europarl.europa.eu/plenary/en/debates-video.html. As of June 2024 this method wasn't functioning anymore, with the Multimedia Center option being the only one available.

Then we need to separate the audio tracks we're interested in. First let's list the audio tracks:

`ffmpeg -i /yourpath/eptic-pipeline/data/0001.wmv` 

If video is `.wav`, here is how we can get the Italian and English audio tracks:

`ffmpeg -i /yourpath/eptic-pipeline/data/0001.wmv -map 0:3 -c:a libmp3lame -q:a 2 italian_track.mp3`
 
`ffmpeg -i /yourpath/eptic-pipeline/data/0001.wmv -map 0:0 -c:a libmp3lame -q:a 2 english_track.mp3`

If .mp4 it would be:

`ffmpeg -i /yourpath/eptic-pipeline/data/0001.mp4 -map 0:0 -c:a aac -b:a 128k english_track.mp4`

`ffmpeg -i /yourpath/eptic-pipeline/data/0001.mp4 -map 0:3 -c:a aac -b:a 128k italian_track.mp4`


### 2. Transcription

Now that we have an audio for each track we can transcribe them. Recommended software: [**WhisperX**](https://github.com/m-bain/whisperX). Performs transcription and provides timestamps. Installation instructions in the linked page. Transcribing with WhisperX is simple:

`whisperx english_track.mp4`

`whisperx italian_track.mp4`


### 3. Sentence alignment

Recommended software: [**Bertalign**]([https://github.com/m-bain/whisperX](https://github.com/bfsujason/bertalign)). When using Bertalign on previously segmented sentences, set `is_split` to `True` in `aligner.py`. Review sentence alignments. 


### 4. Manual metadata selection and review

Insert ```speech_type``` and other metadata and review transcription. 