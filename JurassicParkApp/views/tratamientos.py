import customtkinter as ctk
from database.conexion import get_connection

class TratamientosView:
    def __init__(self, parent):
        self.parent = parent
        self.dinos  = []
        self.vetes  = []
        self.build()
        self.cargar_tabla()

    def build(self):
        ctk.CTkLabel(self.parent, text="💊  Tratamientos médicos",
                     font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(16,2), anchor="w", padx=24)
        ctk.CTkLabel(self.parent,
                     text="Historial clínico de los dinosaurios",
                     text_color="gray", font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=24, pady=(0,12))

        contenedor = ctk.CTkFrame(self.parent, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=16)

        # ── Tabla ─────────────────────────────────────────
        frame_tabla = ctk.CTkFrame(contenedor)
        frame_tabla.pack(side="left", fill="both", expand=True, padx=(0,8))

        self.scroll = ctk.CTkScrollableFrame(frame_tabla, height=400)
        self.scroll.pack(fill="both", expand=True, padx=8, pady=8)

        for i, col in enumerate(["Fecha","Diagnóstico","Medicamento",
                                  "Dinosaurio","Veterinario"]):
            ctk.CTkLabel(self.scroll, text=col,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="gray"
            ).grid(row=0, column=i, padx=10, pady=4, sticky="w")

        self.filas = []

        # ── Formulario ────────────────────────────────────
        frame_form = ctk.CTkFrame(contenedor, width=300)
        frame_form.pack(side="right", fill="y")
        frame_form.pack_propagate(False)

        ctk.CTkLabel(frame_form, text="Registrar tratamiento",
                     font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(14,10))

        ctk.CTkLabel(frame_form, text="Fecha (YYYY-MM-DD)",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.tf_fecha = ctk.CTkEntry(frame_form, width=265,
                                     placeholder_text="2025-06-01")
        self.tf_fecha.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Diagnóstico",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.tf_diag = ctk.CTkEntry(frame_form, width=265,
                                    placeholder_text="Ej: Chequeo general")
        self.tf_diag.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Medicamento",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.cb_med = ctk.CTkComboBox(frame_form, width=265, values=[
            "Sin medicacion", "Suplemento vitaminico",
            "Sedante controlado", "Antibiotico preventivo",
            "Antiinflamatorio", "Vitaminas"
        ])
        self.cb_med.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Observaciones",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.tf_obs = ctk.CTkEntry(frame_form, width=265,
                                   placeholder_text="Notas adicionales...")
        self.tf_obs.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Dinosaurio",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.cb_dino = ctk.CTkComboBox(frame_form, width=265, values=[])
        self.cb_dino.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Veterinario",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.cb_vete = ctk.CTkComboBox(frame_form, width=265, values=[])
        self.cb_vete.pack(padx=14)

        ctk.CTkButton(frame_form, text="💾  Guardar",
                      command=self.guardar, height=38,
                      font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=14, padx=14, fill="x")

        self.lbl_msg = ctk.CTkLabel(frame_form, text="",
                                    font=ctk.CTkFont(size=12))
        self.lbl_msg.pack()

        self.cargar_combos()

    def cargar_combos(self):
        try:
            conn = get_connection()
            cur  = conn.cursor()

            cur.execute(
                "SELECT codDino, nombre FROM Dinosaurio ORDER BY nombre")
            self.dinos = cur.fetchall()
            self.cb_dino.configure(values=[d.nombre for d in self.dinos])
            if self.dinos: self.cb_dino.set(self.dinos[0].nombre)

            cur.execute("""
                SELECT MatriculaVete,
                       nombre + ' ' + apellido AS fullname
                FROM   Veterinario ORDER BY nombre
            """)
            self.vetes = cur.fetchall()
            self.cb_vete.configure(
                values=[v.fullname for v in self.vetes])
            if self.vetes: self.cb_vete.set(self.vetes[0].fullname)

            conn.close()
        except Exception as ex:
            self.lbl_msg.configure(text=f"Error: {ex}",
                                   text_color="orange")

    def cargar_tabla(self):
        for ws in self.filas:
            for w in ws: w.destroy()
        self.filas = []
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT t.fecha, t.diagnostico, t.medicamento,
                       d.nombre  AS dino,
                       v.nombre + ' ' + v.apellido AS vete
                FROM   TratamientoMedico t
                JOIN   Dinosaurio  d ON t.codDino       = d.codDino
                JOIN   Veterinario v ON t.MatriculaVete = v.MatriculaVete
                ORDER  BY t.fecha DESC
            """)
            for r, fila in enumerate(cur.fetchall(), 1):
                ws = []
                for c, val in enumerate([
                    str(fila.fecha)[:10], fila.diagnostico,
                    fila.medicamento, fila.dino, fila.vete
                ]):
                    lbl = ctk.CTkLabel(self.scroll, text=val,
                                       font=ctk.CTkFont(size=12))
                    lbl.grid(row=r, column=c, padx=10, pady=3, sticky="w")
                    ws.append(lbl)
                self.filas.append(ws)
            conn.close()
        except Exception as ex:
            self.lbl_msg.configure(text=f"Error: {ex}",
                                   text_color="#E24B4A")

    def guardar(self):
        fecha  = self.tf_fecha.get().strip()
        diag   = self.tf_diag.get().strip()
        med    = self.cb_med.get()
        obs    = self.tf_obs.get().strip()
        dino_n = self.cb_dino.get()
        vete_n = self.cb_vete.get()

        if not all([fecha, diag, obs]):
            self.lbl_msg.configure(
                text="⚠️  Completá todos los campos", text_color="orange")
            return
        try:
            cod_dino = next(d.codDino for d in self.dinos
                            if d.nombre == dino_n)
            mat_vete = next(v.MatriculaVete for v in self.vetes
                            if v.fullname == vete_n)
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO TratamientoMedico
                    (fecha, diagnostico, medicamento,
                     observaciones, codDino, MatriculaVete)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (fecha, diag, med, obs, cod_dino, mat_vete))
            conn.commit()
            conn.close()
            self.lbl_msg.configure(text="✅  Guardado correctamente",
                                   text_color="#1D9E75")
            self.tf_fecha.delete(0, "end")
            self.tf_diag.delete(0, "end")
            self.tf_obs.delete(0, "end")
            self.cargar_tabla()
        except Exception as ex:
            self.lbl_msg.configure(text=f"❌  {ex}",
                                   text_color="#E24B4A")