import os, pathlib
import subprocess


class Converter():
    def __init__(self, vid_file_path):
        self.video_path = pathlib.Path(vid_file_path)
        self.audio_path = self.video_path.with_suffix(".mp3")
    
    def convert_vid_to_aud(
        self,
        ac=1, #audio channels
        ar=16000, #audio sample rate. for this proj, i'm using 16khz
        bitrate="192k"):
        
        if not os.path.isfile(self.video_path):
            print("file doesn't exist")
            return
        
        command = f"ffmpeg -y -i {self.video_path} -vn -ar {ar} -ac {ac} -b:a {bitrate} {self.audio_path}"
        try:
            subprocess.run(command, capture_output=True,  shell=True)
            print(f"successfully converted {self.video_path} to {self.audio_path}")
            result = {
                "audio_file": self.audio_path,
                "source_file": self.video_path
            }
            return result
            
        except subprocess.CalledProcessError as e:
            print(F"An error occured while converting {self.video_path} to mp3\nError msg: {e.output.decode()}")        