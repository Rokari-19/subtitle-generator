import mlx_whisper

from tempfile import NamedTemporaryFile


class speechToTextGenerator():
    def __init__(self, model:str):
        self.model = model

    def transcribe(self, file: str):
        transcription = mlx_whisper.transcribe(
            file, path_or_hf_repo=self.model, fp16=True, word_timestamps=True
        )

        return transcription

# process = transcribe("audio", "mlx-community/whisper-base")
# print(process)