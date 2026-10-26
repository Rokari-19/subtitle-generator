from decoder import transcription, videoconverter
from pathlib import Path

def main():
    converter = videoconverter.Converter("videosample.mov")
    result = converter.convert_vid_to_aud()
    audio_file = str(result["audio_file"]) # type: ignore
    print(type(audio_file))
    

    file_path = audio_file
    generator = transcription.speechToTextGenerator(model="mlx-community/whisper-base-mlx")
    process = generator.transcribe(file=file_path)
    
    with open("process.txt", "w", encoding="utf-8") as file:
        file.write(str(process))
        
            
        
if __name__ == "__main__":
    main()