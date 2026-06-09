import customtkinter as ctk
from database.conexion import get_connection

class DinosauriosView:
    def __init__(self, parent):
        self.parent = parent
        self.especies  = []
        self.habitats  = []
        self.build()
        self.cargar_tabla()

    def build(self):
        ctk.CTkLabel(self.parent, text="🦖  Dinosaurios",
                     font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(16,2), anchor="w", padx=24)
        ctk.CTkLabel(self.parent, text="Gestioná los dinosaurios del parque",
                     text_color="gray", font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=24, pady=(0,12))

        # ── Layout: tabla izquierda | formulario derecha ──
        contenedor = ctk.CTkFrame(self.parent, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=16, pady=4)

        # ── TABLA (izquierda) ─────────────────────────────
        frame_tabla = ctk.CTkFrame(contenedor)
        frame_tabla.pack(side="left", fill="both", expand=True, padx=(0,8))

        ctk.CTkLabel(frame_tabla, text="Dinosaurios registrados",
                     font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(12,6), padx=12, anchor="w")

        import tkinter as tk
        self.tree_frame = ctk.CTkScrollableFrame(frame_tabla, height=400)
        self.tree_frame.pack(fill="both", expand=True, padx=8, pady=(0,8))

        cols = ["Nombre","Sexo","Peso(kg)","Estado","Especie","Hábitat"]
        for i, c in enumerate(cols):
            ctk.CTkLabel(self.tree_frame, text=c,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="gray"
            ).grid(row=0, column=i, padx=6, pady=4, sticky="w")

        self.filas = []

        # Botón eliminar
        ctk.CTkButton(frame_tabla, text="🗑  Eliminar seleccionado",
                      command=self.eliminar, fg_color="#7f1d1d",
                      hover_color="#991b1b", height=32
        ).pack(pady=(0,10))

        # ── FORMULARIO (derecha) ──────────────────────────
        frame_form = ctk.CTkFrame(contenedor, width=320)
        frame_form.pack(side="right", fill="y")
        frame_form.pack_propagate(False)

        ctk.CTkLabel(frame_form, text="Registrar nuevo dinosaurio",
                     font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(14,10), padx=12)

        campos = [
            ("Nombre",          "tf_nombre",  "entry",  None),
            ("Sexo",            "cb_sexo",    "combo",  ["M","F"]),
            ("Fecha nacimiento","tf_fecha",   "entry",  None),
            ("Peso (kg)",       "tf_peso",    "entry",  None),
            ("Altura (m)",      "tf_altura",  "entry",  None),
            ("Estado de salud", "cb_estado",  "combo",
             ["Estable","Observacion","Agresivo","Critico"]),
            ("Especie",         "cb_especie", "combo",  []),
            ("Hábitat",         "cb_habitat", "combo",  []),
        ]
        for label, attr, tipo, opts in campos:
            ctk.CTkLabel(frame_form, text=label,
                         font=ctk.CTkFont(size=12), anchor="w"
            ).pack(fill="x", padx=14, pady=(6,0))
            if tipo == "entry":
                widget = ctk.CTkEntry(frame_form, width=280,
                                      placeholder_text=label)
            else:
                widget = ctk.CTkComboBox(frame_form, width=280,
                                         values=opts or [])
            widget.pack(padx=14, pady=(2,0))
            setattr(self, attr, widget)

        ctk.CTkButton(frame_form, text="💾  Guardar en base de datos",
                      command=self.guardar, height=38,
                      font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=14, padx=14, fill="x")

        self.lbl_msg = ctk.CTkLabel(frame_form, text="",
                                    font=ctk.CTkFont(size=12))
        self.lbl_msg.pack()

        # Cargar combos desde la BD
        self.cargar_combos()

    def cargar_combos(self):
        try:
            conn = get_connection()
            cur  = conn.cursor()

            cur.execute("SELECT codEspecie, nombre FROM Especie ORDER BY nombre")
            self.especies = cur.fetchall()
            self.cb_especie.configure(
                values=[r.nombre for r in self.especies])
            if self.especies:
                self.cb_especie.set(self.especies[0].nombre)

            cur.execute("SELECT codHabitat, nombre FROM Habitat ORDER BY nombre")
            self.habitats = cur.fetchall()
            self.cb_habitat.configure(
                values=[r.nombre for r in self.habitats])
            if self.habitats:
                self.cb_habitat.set(self.habitats[0].nombre)

            conn.close()
        except Exception as e:
            self.lbl_msg.configure(
                text=f"Error cargando combos: {e}", text_color="orange")

    def cargar_tabla(self):
        # Limpia filas anteriores
        for widgets in self.filas:
            for w in widgets:
                w.destroy()
        self.filas = []

        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT d.codDino, d.nombre, d.sexo, d.peso, d.estadoSalud,
                       e.nombre AS especie, h.nombre AS habitat
                FROM   Dinosaurio d
                JOIN   Especie  e ON d.codEspecie  = e.codEspecie
                JOIN   Habitat  h ON d.codHabitat  = h.codHabitat
                ORDER  BY d.nombre
            """)
            filas = cur.fetchall()
            conn.close()

            self.ids_filas = []
            for r, fila in enumerate(filas, start=1):
                self.ids_filas.append(fila.codDino)
                vals = [fila.nombre, fila.sexo, str(fila.peso),
                        fila.estadoSalud, fila.especie, fila.habitat]
                widgets_fila = []
                for c, val in enumerate(vals):
                    color = "white"
                    if val == "Agresivo": color = "#fca5a5"
                    if val == "Observacion": color = "#fde68a"
                    lbl = ctk.CTkLabel(self.tree_frame, text=val,
                                       font=ctk.CTkFont(size=12),
                                       text_color=color if val in
                                       ["Agresivo","Observacion"] else None)
                    lbl.grid(row=r, column=c, padx=6, pady=3, sticky="w")
                    lbl.bind("<Button-1>",
                             lambda e, idx=r-1: self.seleccionar(idx))
                    widgets_fila.append(lbl)
                self.filas.append(widgets_fila)

        except Exception as e:
            self.lbl_msg.configure(
                text=f"Error: {e}", text_color="#E24B4A")

        self.seleccionado = None

    def seleccionar(self, idx):
        self.seleccionado = idx
        self.lbl_msg.configure(
            text=f"✔ Fila {idx+1} seleccionada", text_color="gray")

    def guardar(self):
        nombre  = self.tf_nombre.get().strip()
        sexo    = self.cb_sexo.get()
        fecha   = self.tf_fecha.get().strip()
        peso    = self.tf_peso.get().strip()
        altura  = self.tf_altura.get().strip()
        estado  = self.cb_estado.get()

        especie_nombre = self.cb_especie.get()
        habitat_nombre = self.cb_habitat.get()

        if not all([nombre, sexo, fecha, peso, altura]):
            self.lbl_msg.configure(
                text="⚠️  Completá todos los campos", text_color="orange")
            return

        try:
            cod_especie = next(
                r.codEspecie for r in self.especies
                if r.nombre == especie_nombre)
            cod_habitat = next(
                r.codHabitat for r in self.habitats
                if r.nombre == habitat_nombre)

            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO Dinosaurio
                    (nombre, sexo, fechaNacimiento, peso, altura,
                     estadoSalud, codEspecie, codHabitat)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nombre, sexo, fecha,
                  float(peso), float(altura),
                  estado, cod_especie, cod_habitat))
            conn.commit()
            conn.close()

            self.lbl_msg.configure(
                text="✅  Guardado correctamente", text_color="#1D9E75")
            self.tf_nombre.delete(0,"end")
            self.tf_fecha.delete(0,"end")
            self.tf_peso.delete(0,"end")
            self.tf_altura.delete(0,"end")
            self.cargar_tabla()

        except Exception as e:
            self.lbl_msg.configure(
                text=f"❌  Error: {e}", text_color="#E24B4A")

    def eliminar(self):
        if self.seleccionado is None:
            self.lbl_msg.configure(
                text="⚠️  Seleccioná una fila primero", text_color="orange")
            return
        cod = self.ids_filas[self.seleccionado]
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute(
                "DELETE FROM Dinosaurio WHERE codDino = ?", (cod,))
            conn.commit()
            conn.close()
            self.lbl_msg.configure(
                text="🗑  Eliminado correctamente", text_color="#1D9E75")
            self.seleccionado = None
            self.cargar_tabla()
        except Exception as e:
            self.lbl_msg.configure(
                text=f"❌  Error: {e}", text_color="#E24B4A")