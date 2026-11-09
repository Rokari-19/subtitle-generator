import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audio_enc.decoder.videoconverter import Converter


class ConverterTests(unittest.TestCase):
    def test_passes_paths_as_arguments_without_shell_interpolation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "source video.mov"
            source_path.touch()

            with patch("audio_enc.decoder.videoconverter.subprocess.run") as run:
                result = Converter(source_path).convert_vid_to_aud()

        command = run.call_args.args[0]
        self.assertIsInstance(command, list)
        self.assertEqual(command[command.index("-i") + 1], str(source_path))
        self.assertEqual(result["audio_file"], source_path.with_suffix(".mp3"))
        self.assertTrue(run.call_args.kwargs["check"])

    def test_reports_a_missing_source_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "missing.mov"

            with self.assertRaises(FileNotFoundError):
                Converter(source_path).convert_vid_to_aud()


if __name__ == "__main__":
    unittest.main()
