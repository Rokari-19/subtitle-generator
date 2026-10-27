from customtkinter import CTk, CTkButton, CTkLabel, CTkFont
from pathlib import Path
from decoder import transcription, videoconverter
from tkinter import * # type: ignore 
from tkinter import filedialog, messagebox

class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.geometry("400x400")
        # set_appearance_mode("system")
        # set_default_color_theme("green")
        self.generator_label = CTkLabel(
            self,
            text="Subtitle Generator",
            
        )
        self.generator_label.pack(side=TOP, pady=60)
        
        
        self.import_button = CTkButton(
            self,
            width=60, 
            text="Import file",
            command=self.import_file_callback,
            fg_color="#323335", 
            hover_color="grey", 
            corner_radius=50,
            font=(CTkFont(family="Mistral", size=12, weight="normal", slant="italic"))
        )
        self.import_button.pack(pady=10, padx=65)
        
        self.generate_button = CTkButton(
            self,
            width=60, 
            text="Generate",
            command=self.generate_subtitles,
            fg_color="#323335", 
            hover_color="grey", 
            corner_radius=50,
            font=(CTkFont(family="Mistral", size=12, weight="normal", slant="italic"))
        )
        self.generate_button.pack(pady=10, padx=65)
        
    def import_file_callback(self):
        filetypes = (
            ("media files", "*.mp4 *.mkv"),
        )
        self.filename = filedialog.askopenfilename(
            title="Select video File",
            initialdir=Path.home() / "Downloads",
            filetypes=filetypes
        )
        
        messagebox.showinfo(
            title="selected file",
            message=self.filename
        )
        
    def generate_subtitles(self):
        converter = videoconverter.Converter(self.filename)
        result = converter.convert_vid_to_aud()
        audio_file = str(result["audio_file"]) # type: ignore
        # print(type(audio_file))
        

        file_path = audio_file
        generator = transcription.speechToTextGenerator(model="mlx-community/whisper-base-mlx")
        process = generator.transcribe(file=file_path)
        
        with open("process.txt", "w", encoding="utf-8") as file:
            file.write(str(process))