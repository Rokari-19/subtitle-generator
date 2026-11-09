import logging
import os
import queue
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path

from customtkinter import CTk, CTkButton, CTkFont, CTkFrame, CTkLabel, CTkTextbox
from tkinter import filedialog


@dataclass(frozen=True)
class GenerationSuccess:
    output_path: Path
    preview: str
    backend: str


@dataclass(frozen=True)
class GenerationFailure:
    error: str


def get_log_file_path() -> Path:
    if sys.platform == "darwin":
        log_directory = Path.home() / "Library" / "Logs" / "Audio Enc"
    elif os.name == "nt":
        log_directory = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Audio Enc" / "Logs"
    else:
        state_directory = Path(
            os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")
        )
        log_directory = state_directory / "audio-enc"

    log_directory.mkdir(parents=True, exist_ok=True)
    return log_directory / "subtitle-generator.log"


class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Subtitle Generator")
        self.geometry("760x640")
        self.minsize(600, 480)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.filename: Path | None = None
        self.output_path: Path | None = None
        self.worker: threading.Thread | None = None
        self.worker_events: queue.Queue[GenerationSuccess | GenerationFailure] = (
            queue.Queue()
        )
        self.app_logger = logging.getLogger("audio_enc")
        self.app_logger.setLevel(logging.INFO)
        self.app_logger.propagate = False
        self.log_path = get_log_file_path()
        self.log_handler = logging.FileHandler(
            self.log_path, encoding="utf-8", delay=False
        )
        self.log_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        self.app_logger.addHandler(self.log_handler)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.generator_label = CTkLabel(
            self,
            text="Subtitle Generator",
            font=CTkFont(family="Arial", size=28, weight="bold"),
        )
        self.generator_label.grid(row=0, column=0, padx=24, pady=(28, 8))

        controls = CTkFrame(self)
        controls.grid(row=1, column=0, sticky="ew", padx=24, pady=12)
        controls.grid_columnconfigure(0, weight=1)
        controls.grid_columnconfigure(1, weight=1)

        self.import_button = CTkButton(
            controls,
            text="Import video",
            command=self.import_file_callback,
            fg_color="#315c8c",
            hover_color="#264a70",
            corner_radius=8,
            font=CTkFont(family="Arial", size=14, weight="bold"),
        )
        self.import_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.generate_button = CTkButton(
            controls,
            text="Generate subtitles",
            command=self.generate_subtitles,
            fg_color="#2e7d5b",
            hover_color="#246347",
            corner_radius=8,
            font=CTkFont(family="Arial", size=14, weight="bold"),
            state="disabled",
        )
        self.generate_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        self.selected_label = CTkLabel(self, text="No video selected", anchor="w")
        self.selected_label.grid(row=2, column=0, sticky="ew", padx=28, pady=(4, 8))

        self.preview = CTkTextbox(self, wrap="word", font=CTkFont(size=13))
        self.preview.grid(row=3, column=0, sticky="nsew", padx=24, pady=8)
        self.preview.insert("1.0", "Generated subtitles will appear here.")
        self.preview.configure(state="disabled")

        footer = CTkFrame(self)
        footer.grid(row=4, column=0, sticky="ew", padx=24, pady=(8, 20))
        footer.grid_columnconfigure(0, weight=1)

        self.status_label = CTkLabel(
            footer, text="Choose a video to get started.", anchor="w"
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.open_log_button = CTkButton(
            footer,
            text="Open log file",
            width=110,
            command=self.open_log_file,
            fg_color="#323335",
            hover_color="#4a4b4d",
            corner_radius=8,
            font=CTkFont(family="Arial", size=12),
        )
        self.open_log_button.grid(row=0, column=1, padx=(0, 8))

        self.open_output_button = CTkButton(
            footer,
            text="Open SRT",
            width=100,
            command=self.open_output_file,
            state="disabled",
            fg_color="#323335",
            hover_color="#4a4b4d",
            corner_radius=8,
            font=CTkFont(family="Arial", size=12),
        )
        self.open_output_button.grid(row=0, column=2)
        self.app_logger.info("Application ready.")
        self.app_logger.info("Log file: %s", self.log_path)
        self.after(100, self._drain_worker_events)

    def import_file_callback(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select a video file",
            initialdir=Path.home() / "Downloads",
            filetypes=(
                (
                    "Video files",
                    "*.mp4 *.mkv *.mov *.avi *.webm *.m4v *.MP4 *.MKV *.MOV *.AVI *.WEBM *.M4V",
                ),
                ("All files", "*.*"),
            ),
        )
        if not filename:
            self.app_logger.info("Video selection cancelled.")
            return

        self.filename = Path(filename)
        self.app_logger.info("Selected video: %s", self.filename)
        self.selected_label.configure(text=f"Selected: {self.filename.name}")
        self.status_label.configure(text="Ready to generate subtitles.")
        self.generate_button.configure(state="normal")
        self.open_output_button.configure(state="disabled")

    def generate_subtitles(self) -> None:
        if self.filename is None:
            self.app_logger.error("Cannot generate subtitles: no video selected.")
            self.status_label.configure(text="Import a video before generating subtitles.")
            return

        source_path = self.filename
        self.app_logger.info("Starting subtitle generation for %s", source_path)
        self._set_busy(True)
        self.status_label.configure(text="Starting subtitle generation...")
        worker = threading.Thread(
            target=self._generate_worker,
            args=(source_path,),
            name="subtitle-generation",
            daemon=True,
        )
        self.worker = worker
        try:
            worker.start()
        except RuntimeError as error:
            self.app_logger.exception("Could not start subtitle worker.")
            self._set_busy(False)
            self.status_label.configure(text=f"Could not start: {error}")

    def _generate_worker(self, source_path: Path) -> None:
        try:
            from audio_enc.decoder.transcription import (
                transcribe_with_fallback,
                write_srt,
            )
            from audio_enc.decoder.videoconverter import Converter

            converted = Converter(source_path).convert_vid_to_aud()
            self.app_logger.info("Audio extracted to %s", converted["audio_file"])
            self.app_logger.info("Starting speech recognition.")
            transcription, backend = transcribe_with_fallback(converted["audio_file"])
            self.app_logger.info(
                "Transcription finished with %s (%d segments).",
                backend,
                len(transcription["segments"]),
            )
            output_path = write_srt(transcription, source_path.with_suffix(".srt"))
            preview = output_path.read_text(encoding="utf-8")
        except Exception as error:
            self.app_logger.exception("Subtitle generation failed.")
            self.worker_events.put(GenerationFailure(str(error)))
            return

        self.worker_events.put(GenerationSuccess(output_path, preview, backend))

    def _drain_worker_events(self) -> None:
        while True:
            try:
                event = self.worker_events.get_nowait()
            except queue.Empty:
                break

            if isinstance(event, GenerationFailure):
                if self.worker is not None:
                    self.worker.join()
                self._show_failure(event.error)
            else:
                if self.worker is not None:
                    self.worker.join()
                self._show_success(event.output_path, event.preview, event.backend)

        self.after(100, self._drain_worker_events)

    def _set_busy(self, busy: bool) -> None:
        self.import_button.configure(state="disabled" if busy else "normal")
        self.generate_button.configure(
            state="disabled" if busy or self.filename is None else "normal"
        )

    def _show_failure(self, error: str) -> None:
        self._set_busy(False)
        self.status_label.configure(text=f"Generation failed: {error}")

    def _show_success(self, output_path: Path, preview: str, backend: str) -> None:
        self._set_busy(False)
        self.output_path = output_path
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", preview or "No speech was detected.")
        self.preview.configure(state="disabled")
        self.open_output_button.configure(state="normal")
        self.status_label.configure(text=f"{backend}: saved {output_path.name}")
        self.app_logger.info("Subtitle file saved to %s", output_path)

    def open_output_file(self) -> None:
        if self.output_path is None:
            return
        self._open_file(self.output_path)

    def open_log_file(self) -> None:
        self.log_handler.flush()
        self._open_file(self.log_path)

    def _open_file(self, path: Path) -> None:
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            elif os.name == "nt":
                os.startfile(path)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except OSError:
            self.app_logger.exception("Could not open file: %s", path)
            self.status_label.configure(text=f"Could not open file: {path}")

    def close(self) -> None:
        if self.worker is not None and self.worker.is_alive():
            self.app_logger.warning(
                "Wait for subtitle generation to finish before closing."
            )
            self.status_label.configure(
                text="Please wait for subtitle generation to finish before closing."
            )
            return
        self.app_logger.removeHandler(self.log_handler)
        self.log_handler.flush()
        self.log_handler.close()
        self.destroy()
