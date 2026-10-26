from typing import Any, Tuple

import customtkinter as ctk

class widowFrame(ctk.CTkFrame):
    def __init__(self, master, width, height):
        
        
        super().__init__(master, width, height)
        
        

class Button(ctk.CTkButton):
    def __init__(self, master, text="", command=None, **kwargs):
        
        default_fg_color = "#2196F3"  
        default_hover_color = "#1976D2"
        
        kwargs.setdefault("fgcolor", default_fg_color)
        kwargs.setdefault("hover_color", default_hover_color)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("font", ctk.CTkFont(family="Proxima Nova", size=13, weight="bold"))
        
        super().__init__(master, text=text, command=command)

