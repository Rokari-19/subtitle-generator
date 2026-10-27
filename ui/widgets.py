# from typing import Any, Tuple

# import customtkinter as ctk

# class widowFrame(ctk.CTkFrame):
#     def __init__(self, master, width, height):
        
        
#         super().__init__(master, width, height)
        
        

# class Button(ctk.CTkButton):
#     def __init__(self, master, text="", command=None, **kwargs):
        
#         default_fg_color = "#323335"  
#         default_hover_color = "#1976D2"
        
#         kwargs.setdefault("fgcolor", default_fg_color)
#         kwargs.setdefault("hover_color", default_hover_color)
#         kwargs.setdefault("corner_radius", 8)
#         kwargs.setdefault("font", ctk.CTkFont(family="Mistral", size=16, weight="bold"))
        
#         super().__init__(master, text=text, command=command)

# # class StyledButton(ctk.CTkButton):
# #     """A customized button with consistent styling"""
    
# #     def __init__(self, parent, text="Button", style="primary", **kwargs):
# #         # Define color schemes
# #         styles = {
# #             "primary": {"bg": "#007bff", "fg": "white", "activebackground": "#0056b3"},
# #             "success": {"bg": "#28a745", "fg": "white", "activebackground": "#1e7e34"},
# #             "danger": {"bg": "#dc3545", "fg": "white", "activebackground": "#bd2130"}
# #         }
        
# #         # Apply style
# #         style_config = styles.get(style, styles["primary"])
# #         default_config = {
# #             "font": ("Mistral", 15, "bold"),
# #             "relief": "flat",
# #             "bd": 0,
# #             "padx": 20,
# #             "pady": 5,
# #             "cursor": "hand2"
# #         }
        
# #         # Merge configurations
# #         config = {**default_config, **style_config, **kwargs}
        
# #         super().__init__(parent, text=text, **config)