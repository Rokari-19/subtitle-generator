# Audio Enc

Audio Enc is a desktop app that extracts audio from a video, transcribes speech,
and creates a time-coded SubRip (`.srt`) subtitle file.

## Requirements

- Python 3.14 or newer
- [FFmpeg](https://ffmpeg.org/) available on `PATH`
- macOS, Windows, or Linux with a graphical desktop

Choose Faster-Whisper (CPU) or MLX-Whisper from the model selector in the app.
MLX-Whisper requires Apple silicon and macOS.

## Install

Install [uv](https://docs.astral.sh/uv/) and clone this repository, then run:

```sh
uv sync
```

To install MLX-Whisper on Apple silicon:

```sh
uv sync --extra mlx
```

FFmpeg is a separate system dependency; install it with your operating system's
package manager if it is not already available.

## Run

```sh
uv run audio-enc
```
You can build an executable for your platorm with:

```sh
uv run pyinstaller --windowed main.py
```

You can also run `uv run python main.py` from the repository. In the app, import
a video and choose **Generate subtitles**. The first transcription may take
longer while the selected speech-recognition model is downloaded.

The app accepts common FFmpeg-supported video files, including MP4, MKV, MOV,
AVI, WebM, and M4V. It saves the extracted audio and `.srt` file beside the
source video, displays the subtitles in the app, and provides **Open SRT** and
**Open log file** buttons. Logs are written to `~/Library/Logs/Audio Enc/` on
macOS, `%LOCALAPPDATA%/Audio Enc/Logs/` on Windows, or
`$XDG_STATE_HOME/audio-enc/` on Linux (defaulting to `~/.local/state/audio-enc/`).

## Development

Run the test suite with:

```sh
uv run python -m unittest discover -s tests
```