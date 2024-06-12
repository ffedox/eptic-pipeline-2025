# WhisperX

Automatic Speech Recognition with Word-level Timestamps (& Diarization).

conda create --name whisperx-eptic

conda activate whisperx-eptic

pip install torch==2.0.0+cu117 torchaudio==2.0.0+cu117 -f https://download.pytorch.org/whl/torch_stable.html

pip install git+https://github.com/m-bain/whisperx.git

To test run:

whisperx /home/afedotova/eptic-pipeline2/eptic-pipeline3/data/0001.wmv

Conda deactivate to exit