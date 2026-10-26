import ffmpeg

(
    ffmpeg
    .input("input.mp4")
    .output("audio.mp3", acodec="libopus", audio_bitrate="192k")
    .run()
)


# def run():
#     if __name__ == "__main__":
#         pass