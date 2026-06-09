import customtkinter as ctk
from views.dinosaurios   import DinosauriosView
from views.visitantes    import VisitantesView
from views.cuidadores    import CuidadoresView
from views.veterinarios  import VeterinariosView
from views.habitats      import HabitatsView
from views.recorridos    import RecorridosView
from views.alimentacion  import AlimentacionView
from views.tratamientos  import TratamientosView

class HomeView:
    def __init__(self, root):
        self.root = root
        self.build()

    def build(self):
        # ── Sidebar ──────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self.root, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar, text="🦕 Jurassic Park",
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(pady=(28, 6), padx=16)

        ctk.CTkLabel(
            self.sidebar, text="Sistema de Gestión",
            font=ctk.CTkFont(size=11), text_color="gray"
        ).pack(pady=(0, 20))

        secciones = [
            ("🏠  Inicio",             self.show_home),
            ("🦖  Dinosaurios",        lambda: self.show(DinosauriosView)),
            ("🌿  Hábitats",           lambda: self.show(HabitatsView)),
            ("👷  Cuidadores",         lambda: self.show(CuidadoresView)),
            ("🩺  Veterinarios",       lambda: self.show(VeterinariosView)),
            ("🎟️   Visitantes",         lambda: self.show(VisitantesView)),
            ("🚗  Recorridos",         lambda: self.show(RecorridosView)),
            ("🍖  Alimentación",       lambda: self.show(AlimentacionView)),
            ("💊  Tratamientos",       lambda: self.show(TratamientosView)),
        ]
        self.nav_buttons = []
        for texto, cmd in secciones:
            btn = ctk.CTkButton(
                self.sidebar, text=texto, anchor="w",
                command=cmd,
                fg_color="transparent",
                hover_color=("#1b4332", "#1b4332"),
                height=40, font=ctk.CTkFont(size=13)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons.append(btn)

        # ── Área de contenido ─────────────────────────────
        self.content = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.content.pack(side="right", fill="both", expand=True)

        self.show_home()

    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show(self, ViewClass):
        self.clear()
        ViewClass(self.content)

    def show_home(self):
        self.clear()
        ctk.CTkLabel(
            self.content, text="Bienvenido al Sistema de Gestión",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(50, 6))
        ctk.CTkLabel(
            self.content, text="Isla Nublar  ·  Jurassic World",
            font=ctk.CTkFont(size=13), text_color="gray"
        ).pack(pady=(0, 40))

        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.pack()

        tarjetas = [
            ("🦖", "Dinosaurios",   "13 registrados",  "#1D9E75"),
            ("🌿", "Hábitats",      "7 hábitats",      "#378ADD"),
            ("👷", "Cuidadores",    "5 activos",       "#EF9F27"),
            ("🎟️", "Visitantes",    "10 registrados",  "#9F7AEA"),
            ("🩺", "Veterinarios",  "4 especialistas", "#E24B4A"),
            ("🍖", "Alimentación",  "12 registros",    "#1D9E75"),
        ]
        for i, (ico, titulo, sub, color) in enumerate(tarjetas):
            card = ctk.CTkFrame(frame, width=160, height=110, corner_radius=12)
            card.grid(row=i//3, column=i%3, padx=12, pady=12)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=ico, font=ctk.CTkFont(size=24)).pack(pady=(16,2))
            ctk.CTkLabel(card, text=titulo,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=color).pack()
            ctk.CTkLabel(card, text=sub,
                         font=ctk.CTkFont(size=11), text_color="gray").pack()