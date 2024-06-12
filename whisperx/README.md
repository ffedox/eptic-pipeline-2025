# WhisperX

Automatic Speech Recognition with Word-level Timestamps (& Diarization).

conda create --name whisperx 

conda activate whisperx

pip install torch==2.0.0+cu117 torchaudio==2.0.0+cu117 -f https://download.pytorch.org/whl/torch_stable.html

pip install git+https://github.com/m-bain/whisperx.git

To test run:

whisperx /home/afedotova/eptic-pipeline/eptic-pipeline/example/data/videos/english_track.mp3

