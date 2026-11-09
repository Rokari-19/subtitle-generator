import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class Converter:
    def __init__(self, vid_file_path: str | Path) -> None:
        self.video_path = Path(vid_file_path)
        self.audio_path = self.video_path.with_suffix(".mp3")

    def convert_vid_to_aud(
        self,
        ac: int = 1,
        ar: int = 16000,
        bitrate: str = "192k",
    ) -> dict[str, Path]:
        if not self.video_path.is_file():
            raise FileNotFoundError(f"Media file does not exist: {self.video_path}")

        logger.info("Extracting audio from %s.", self.video_path)
        command = [
            "ffmpeg",
            "-y",
            "-nostdin",
            "-i",
            str(self.video_path),
            "-vn",
            "-ar",
            str(ar),
            "-ac",
            str(ac),
            "-b:a",
            bitrate,
            str(self.audio_path),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as error:
            detail = error.stderr.strip() if error.stderr else str(error)
            logger.error("FFmpeg failed: %s", detail)
            raise RuntimeError(
                f"Could not convert {self.video_path} to audio: {detail}"
            ) from error

        logger.info("Audio extraction completed: %s.", self.audio_path)
        return {
            "audio_file": self.audio_path,
            "source_file": self.video_path,
        }