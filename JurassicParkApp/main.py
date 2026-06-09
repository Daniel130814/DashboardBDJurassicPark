import customtkinter as ctk
from views.home import HomeView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("🦕 Jurassic Park – Sistema de Gestión")
app.geometry("1100x680")
app.resizable(False, False)

HomeView(app)
app.mainloop()