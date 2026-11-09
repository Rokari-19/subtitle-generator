import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MLXWhisperGenerator:
    def __init__(self, model: str = "mlx-community/whisper-base-mlx") -> None:
        self.model = model

    def transcribe(self, file: str | Path) -> dict[str, Any]:
        import mlx_whisper

        transcription = mlx_whisper.transcribe(
            str(file), path_or_hf_repo=self.model, fp16=True, word_timestamps=True
        )
        return transcription


# Keep the original class name available to existing imports.
speechToTextGenerator = MLXWhisperGenerator


class FasterWhisperGenerator:
    def __init__(self, model: str = "base") -> None:
        import faster_whisper

        self.model = faster_whisper.WhisperModel(
            model_size_or_path=model,
            device="cpu",
            compute_type="int8",
        )

    def transcribe(self, file: str | Path) -> dict[str, Any]:
        segments, info = self.model.transcribe(
            str(file), word_timestamps=True
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


def transcribe_with_fallback(
    file: str | Path,
    faster_model: str = "base",
    mlx_model: str = "mlx-community/whisper-base-mlx",
) -> tuple[dict[str, Any], str]:
    try:
        logger.info("Loading Faster-Whisper model %s on CPU.", faster_model)
        result = FasterWhisperGenerator(faster_model).transcribe(file)
        return result, "Faster-Whisper"
    except Exception as faster_error:
        logger.exception("Faster-Whisper failed; trying MLX-Whisper fallback.")
        try:
            logger.info("Loading MLX-Whisper model %s.", mlx_model)
            result = MLXWhisperGenerator(mlx_model).transcribe(file)
            return result, "MLX-Whisper fallback"
        except Exception as mlx_error:
            logger.exception("MLX-Whisper fallback failed.")
            raise RuntimeError(
                "Faster-Whisper failed and the MLX-Whisper fallback failed: "
                f"{faster_error}; {mlx_error}"
            ) from mlx_error


def transcribe_with_backend(
    file: str | Path,
    backend: str,
    faster_model: str = "base",
    mlx_model: str = "mlx-community/whisper-base-mlx",
) -> tuple[dict[str, Any], str]:
    if backend == "Faster-Whisper":
        logger.info("Loading Faster-Whisper model %s on CPU.", faster_model)
        return FasterWhisperGenerator(faster_model).transcribe(file), backend
    if backend == "MLX-Whisper":
        logger.info("Loading MLX-Whisper model %s.", mlx_model)
        return MLXWhisperGenerator(mlx_model).transcribe(file), backend
    raise ValueError(f"Unsupported transcription backend: {backend}")


def write_srt(transcription: dict[str, Any], output_path: Path) -> Path:
    import pysubs2

    events = [
        pysubs2.SSAEvent(
            start=pysubs2.make_time(s=float(segment["start"])),
            end=pysubs2.make_time(s=float(segment["end"])),
            text=str(segment.get("text", "")).strip(),
        )
        for segment in transcription["segments"]
    ]
    subtitles = pysubs2.SSAFile()
    subtitles.events.extend(events)
    subtitles.save(str(output_path), format_="srt", encoding="utf-8")
    return output_path
