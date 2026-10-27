import mlx_whisper
import faster_whisper as fsw
from tempfile import NamedTemporaryFile


class speechToTextGenerator():
    def __init__(self, model:str):
        self.model = model

    def transcribe(self, file: str):
        transcription = mlx_whisper.transcribe(
            file, path_or_hf_repo=self.model, fp16=True, word_timestamps=True
        )

        return transcription

class FasterWhisperGenerator():
    def __init__(self, model:str):
        self.model = fsw.WhisperModel(
            model_size_or_path=model,
            device="cpu",
            compute_type="int8",
        )
        
    def transcribe(self, file:str):
        segments, info = self.model.transcribe(
            file, word_timestamps=True
        )
        
        return {
            "language": info.language,
            "segments": [
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "words": [
                        {
                            "start": word.start,
                            "end": word.end,
                            "text": word.word,
                        }
                        for word in (segment.words or [])
                    ],
                }
                for segment in segments
            ],
        }
