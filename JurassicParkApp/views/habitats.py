import customtkinter as ctk
from database.conexion import get_connection

class HabitatsView:
    def __init__(self, parent):
        self.parent = parent
        self.build()
        self.cargar_tabla()

    def build(self):
        ctk.CTkLabel(self.parent, text="🌿  Hábitats",
                     font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(16,2), anchor="w", padx=24)
        ctk.CTkLabel(self.parent, text="Recintos y zonas del parque",
                     text_color="gray", font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=24, pady=(0,12))

        contenedor = ctk.CTkFrame(self.parent, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=16)

        # ── Tabla ─────────────────────────────────────────
        frame_tabla = ctk.CTkFrame(contenedor)
        frame_tabla.pack(side="left", fill="both", expand=True, padx=(0,8))

        self.scroll = ctk.CTkScrollableFrame(frame_tabla, height=400)
        self.scroll.pack(fill="both", expand=True, padx=8, pady=8)

        for i, col in enumerate(["Nombre","Tipo","Capacidad","Temperatura °C"]):
            ctk.CTkLabel(self.scroll, text=col,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="gray"
            ).grid(row=0, column=i, padx=10, pady=4, sticky="w")

        self.filas    = []
        self.ids_fila = []
        self.seleccionado = None

        ctk.CTkButton(frame_tabla, text="🗑  Eliminar seleccionado",
                      command=self.eliminar,
                      fg_color="#7f1d1d", hover_color="#991b1b", height=32
        ).pack(pady=(0,10))

        # ── Formulario ────────────────────────────────────
        frame_form = ctk.CTkFrame(contenedor, width=300)
        frame_form.pack(side="right", fill="y")
        frame_form.pack_propagate(False)

        ctk.CTkLabel(frame_form, text="Registrar hábitat",
                     font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(14,10))

        ctk.CTkLabel(frame_form, text="Nombre",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.tf_nombre = ctk.CTkEntry(frame_form, width=265,
                                      placeholder_text="Ej: Herbivore Plains")
        self.tf_nombre.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Tipo",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.cb_tipo = ctk.CTkComboBox(frame_form, width=265, values=[
            "Recinto de carnivoro", "Recinto de herbivoro",
            "Recinto de entrenamiento", "Recinto de maxima seguridad",
            "Laguna artificial", "Aviario cerrado", "Llanura abierta"
        ])
        self.cb_tipo.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Capacidad",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.tf_cap = ctk.CTkEntry(frame_form, width=265,
                                   placeholder_text="Ej: 10")
        self.tf_cap.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Temperatura (°C)",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.tf_temp = ctk.CTkEntry(frame_form, width=265,
                                    placeholder_text="Ej: 27.5")
        self.tf_temp.pack(padx=14)

        ctk.CTkButton(frame_form, text="💾  Guardar",
                      command=self.guardar, height=38,
                      font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=14, padx=14, fill="x")

        self.lbl_msg = ctk.CTkLabel(frame_form, text="",
                                    font=ctk.CTkFont(size=12))
        self.lbl_msg.pack()

    def cargar_tabla(self):
        for ws in self.filas:
            for w in ws: w.destroy()
        self.filas    = []
        self.ids_fila = []
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT codHabitat, nombre, tipo,
                       capacidad, temperatura
                FROM   Habitat
                ORDER  BY nombre
            """)
            for r, fila in enumerate(cur.fetchall(), 1):
                self.ids_fila.append(fila.codHabitat)
                vals = [fila.nombre, fila.tipo,
                        str(fila.capacidad), str(fila.temperatura)]
                ws = []
                for c, val in enumerate(vals):
                    lbl = ctk.CTkLabel(self.scroll, text=val,
                                       font=ctk.CTkFont(size=12))
                    lbl.grid(row=r, column=c, padx=10, pady=3, sticky="w")
                    lbl.bind("<Button-1>",
                             lambda e, idx=r-1: self.seleccionar(idx))
                    ws.append(lbl)
                self.filas.append(ws)
            conn.close()
        except Exception as ex:
            self.lbl_msg.configure(text=f"Error: {ex}",
                                   text_color="#E24B4A")

    def seleccionar(self, idx):
        self.seleccionado = idx
        self.lbl_msg.configure(
            text=f"✔ Fila {idx+1} seleccionada", text_color="gray")

    def guardar(self):
        nombre = self.tf_nombre.get().strip()
        tipo   = self.cb_tipo.get()
        cap    = self.tf_cap.get().strip()
        temp   = self.tf_temp.get().strip()

        if not all([nombre, cap, temp]):
            self.lbl_msg.configure(
                text="⚠️  Completá todos los campos", text_color="orange")
            return
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO Habitat (nombre, tipo, capacidad, temperatura)
                VALUES (?, ?, ?, ?)
            """, (nombre, tipo, int(cap), float(temp)))
            conn.commit()
            conn.close()
            self.lbl_msg.configure(text="✅  Guardado correctamente",
                                   text_color="#1D9E75")
            self.tf_nombre.delete(0, "end")
            self.tf_cap.delete(0, "end")
            self.tf_temp.delete(0, "end")
            self.cargar_tabla()
        except Exception as ex:
            self.lbl_msg.configure(text=f"❌  {ex}",
                                   text_color="#E24B4A")

    def eliminar(self):
        if self.seleccionado is None:
            self.lbl_msg.configure(
                text="⚠️  Seleccioná una fila primero", text_color="orange")
            return
        cod = self.ids_fila[self.seleccionado]
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute(
                "DELETE FROM Habitat WHERE codHabitat = ?", (cod,))
            conn.commit()
            conn.close()
            self.lbl_msg.configure(text="🗑  Eliminado",
                                   text_color="#1D9E75")
            self.seleccionado = None
            self.cargar_tabla()
        except Exception as ex:
            self.lbl_msg.configure(text=f"❌  {ex}",
                                   text_color="#E24B4A")