from customtkinter import CTk, CTkButton
from widgets import *

class App(CTk):
    def __init__(self, ):
        super().__init__()
        self.geometry("600x600")
        
        
        self.button = CTkButton(self, text="Import Media", command=self.button_callback)
        self.button.pack(padx=20, pady=20)
        
    def button_callback(self):
        print("button_clicked")