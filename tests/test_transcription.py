import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audio_enc.decoder.transcription import (
    transcribe_with_backend,
    transcribe_with_fallback,
    write_srt,
)


class TranscriptionTests(unittest.TestCase):
    def test_selected_faster_whisper_backend_is_used(self) -> None:
        expected = {"segments": []}
        with patch(
            "audio_enc.decoder.transcription.FasterWhisperGenerator"
        ) as faster, patch(
            "audio_enc.decoder.transcription.MLXWhisperGenerator"
        ) as mlx:
            faster.return_value.transcribe.return_value = expected

            result, backend = transcribe_with_backend("input.mp3", "Faster-Whisper")

        self.assertIs(result, expected)
        self.assertEqual(backend, "Faster-Whisper")
        mlx.assert_not_called()

    def test_selected_mlx_backend_is_used(self) -> None:
        expected = {"segments": []}
        with patch(
            "audio_enc.decoder.transcription.FasterWhisperGenerator"
        ) as faster, patch(
            "audio_enc.decoder.transcription.MLXWhisperGenerator"
        ) as mlx:
            mlx.return_value.transcribe.return_value = expected

            result, backend = transcribe_with_backend("input.mp3", "MLX-Whisper")

        self.assertIs(result, expected)
        self.assertEqual(backend, "MLX-Whisper")
        faster.assert_not_called()

    def test_rejects_unknown_backend_without_fallback(self) -> None:
        with patch(
            "audio_enc.decoder.transcription.FasterWhisperGenerator"
        ) as faster, patch(
            "audio_enc.decoder.transcription.MLXWhisperGenerator"
        ) as mlx:
            with self.assertRaisesRegex(ValueError, "Unsupported transcription backend"):
                transcribe_with_backend("input.mp3", "unknown")

        faster.assert_not_called()
        mlx.assert_not_called()

    def test_prefers_faster_whisper(self) -> None:
        expected = {"segments": []}
        with patch(
            "audio_enc.decoder.transcription.FasterWhisperGenerator"
        ) as faster, patch(
            "audio_enc.decoder.transcription.MLXWhisperGenerator"
        ) as mlx, patch("audio_enc.decoder.transcription.logger"):
            faster.return_value.transcribe.return_value = expected

            result, backend = transcribe_with_fallback("input.mp3")

        self.assertIs(result, expected)
        self.assertEqual(backend, "Faster-Whisper")
        mlx.assert_not_called()

    def test_falls_back_to_mlx_when_faster_whisper_fails(self) -> None:
        expected = {"segments": []}
        with patch(
            "audio_enc.decoder.transcription.FasterWhisperGenerator"
        ) as faster, patch(
            "audio_enc.decoder.transcription.MLXWhisperGenerator"
        ) as mlx, patch("audio_enc.decoder.transcription.logger"):
            faster.side_effect = RuntimeError("model unavailable")
            mlx.return_value.transcribe.return_value = expected

            result, backend = transcribe_with_fallback("input.mp3")

        self.assertIs(result, expected)
        self.assertEqual(backend, "MLX-Whisper fallback")

    def test_reports_both_backend_failures(self) -> None:
        with patch(
            "audio_enc.decoder.transcription.FasterWhisperGenerator"
        ) as faster, patch(
            "audio_enc.decoder.transcription.MLXWhisperGenerator"
        ) as mlx, patch("audio_enc.decoder.transcription.logger"):
            faster.side_effect = RuntimeError("faster error")
            mlx.side_effect = RuntimeError("mlx error")

            with self.assertRaisesRegex(RuntimeError, "faster error; mlx error"):
                transcribe_with_fallback("input.mp3")

    def test_writes_srt_with_timestamped_subtitles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "captions.srt"
            write_srt(
                {
                    "segments": [
                        {"start": 1.0, "end": 2.5, "text": " Hello world! "}
                    ]
                },
                output_path,
            )

            contents = output_path.read_text(encoding="utf-8")

        self.assertIn("00:00:01,000 --> 00:00:02,500", contents)
        self.assertIn("Hello world!", contents)


if __name__ == "__main__":
    unittest.main()
