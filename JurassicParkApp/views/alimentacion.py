import customtkinter as ctk
from database.conexion import get_connection

class AlimentacionView:
    def __init__(self, parent):
        self.parent = parent
        self.dinos = []
        self.cuidadores = []
        self.build()
        self.cargar_tabla()

    def build(self):
        ctk.CTkLabel(self.parent, text="🍖  Alimentación",
                     font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(16,2), anchor="w", padx=24)

        contenedor = ctk.CTkFrame(self.parent, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=16)

        # Tabla
        frame_tabla = ctk.CTkFrame(contenedor)
        frame_tabla.pack(side="left", fill="both", expand=True, padx=(0,8))

        self.scroll = ctk.CTkScrollableFrame(frame_tabla, height=420)
        self.scroll.pack(fill="both", expand=True, padx=8, pady=8)

        for i, col in enumerate(["Fecha","Hora","Tipo comida",
                                  "Cant.(kg)","Dinosaurio","Cuidador"]):
            ctk.CTkLabel(self.scroll, text=col,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="gray"
            ).grid(row=0, column=i, padx=8, pady=4, sticky="w")
        self.filas = []

        # Formulario
        frame_form = ctk.CTkFrame(contenedor, width=300)
        frame_form.pack(side="right", fill="y")
        frame_form.pack_propagate(False)

        ctk.CTkLabel(frame_form, text="Registrar alimentación",
                     font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(14,8))

        ctk.CTkLabel(frame_form, text="Fecha (YYYY-MM-DD)").pack(
            anchor="w", padx=14, pady=(6,0))
        self.tf_fecha = ctk.CTkEntry(frame_form, width=260,
                                     placeholder_text="2025-06-01")
        self.tf_fecha.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Hora (HH:MM)").pack(
            anchor="w", padx=14, pady=(6,0))
        self.tf_hora = ctk.CTkEntry(frame_form, width=260,
                                    placeholder_text="08:00")
        self.tf_hora.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Tipo de comida").pack(
            anchor="w", padx=14, pady=(6,0))
        self.cb_tipo = ctk.CTkComboBox(
            frame_form, width=260,
            values=["Carne vacuna","Carne de cerdo","Pescado",
                    "Tiburon","Vegetacion fresca","Hojas y ramas",
                    "Helechos","Pescado pequeño"])
        self.cb_tipo.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Cantidad (kg)").pack(
            anchor="w", padx=14, pady=(6,0))
        self.tf_cant = ctk.CTkEntry(frame_form, width=260,
                                    placeholder_text="Ej: 120")
        self.tf_cant.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Dinosaurio").pack(
            anchor="w", padx=14, pady=(6,0))
        self.cb_dino = ctk.CTkComboBox(frame_form, width=260, values=[])
        self.cb_dino.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Cuidador").pack(
            anchor="w", padx=14, pady=(6,0))
        self.cb_cuid = ctk.CTkComboBox(frame_form, width=260, values=[])
        self.cb_cuid.pack(padx=14)

        ctk.CTkButton(frame_form, text="💾  Guardar",
                      command=self.guardar, height=38
        ).pack(pady=14, padx=14, fill="x")

        self.lbl_msg = ctk.CTkLabel(frame_form, text="")
        self.lbl_msg.pack()

        self.cargar_combos()

    def cargar_combos(self):
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("SELECT codDino, nombre FROM Dinosaurio ORDER BY nombre")
            self.dinos = cur.fetchall()
            self.cb_dino.configure(values=[d.nombre for d in self.dinos])
            if self.dinos: self.cb_dino.set(self.dinos[0].nombre)

            cur.execute("""SELECT LegajoCuidador, nombre + ' ' + apellido AS fullname
                           FROM Cuidador ORDER BY nombre""")
            self.cuidadores = cur.fetchall()
            self.cb_cuid.configure(
                values=[c.fullname for c in self.cuidadores])
            if self.cuidadores: self.cb_cuid.set(self.cuidadores[0].fullname)
            conn.close()
        except Exception as e:
            self.lbl_msg.configure(text=f"Error: {e}", text_color="orange")

    def cargar_tabla(self):
        for ws in self.filas:
            for w in ws: w.destroy()
        self.filas = []
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT a.fecha, a.hora, a.tipoComida, a.cantidad,
                       d.nombre AS dino,
                       c.nombre + ' ' + c.apellido AS cuidador
                FROM   Alimentacion a
                JOIN   Dinosaurio d ON a.codDino         = d.codDino
                JOIN   Cuidador   c ON a.LegajoCuidador  = c.LegajoCuidador
                ORDER  BY a.fecha DESC, a.hora DESC
            """)
            for r, fila in enumerate(cur.fetchall(), 1):
                ws = []
                for col_i, val in enumerate([
                    str(fila.fecha)[:10], str(fila.hora)[:5],
                    fila.tipoComida, str(fila.cantidad),
                    fila.dino, fila.cuidador]):
                    lbl = ctk.CTkLabel(self.scroll, text=val,
                                       font=ctk.CTkFont(size=12))
                    lbl.grid(row=r, column=col_i,
                             padx=8, pady=3, sticky="w")
                    ws.append(lbl)
                self.filas.append(ws)
            conn.close()
        except Exception as e:
            self.lbl_msg.configure(text=f"Error: {e}", text_color="#E24B4A")

    def guardar(self):
        fecha   = self.tf_fecha.get().strip()
        hora    = self.tf_hora.get().strip()
        tipo    = self.cb_tipo.get()
        cant    = self.tf_cant.get().strip()
        dino_n  = self.cb_dino.get()
        cuid_n  = self.cb_cuid.get()

        if not all([fecha, hora, cant]):
            self.lbl_msg.configure(
                text="⚠️  Completá todos los campos", text_color="orange")
            return
        try:
            cod_dino = next(d.codDino for d in self.dinos
                            if d.nombre == dino_n)
            legajo   = next(c.LegajoCuidador for c in self.cuidadores
                            if c.fullname == cuid_n)
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO Alimentacion
                    (fecha,hora,tipoComida,cantidad,codDino,LegajoCuidador)
                VALUES (?,?,?,?,?,?)
            """, (fecha, hora, tipo, float(cant), cod_dino, legajo))
            conn.commit()
            conn.close()
            self.lbl_msg.configure(
                text="✅  Guardado", text_color="#1D9E75")
            self.tf_fecha.delete(0,"end")
            self.tf_hora.delete(0,"end")
            self.tf_cant.delete(0,"end")
            self.cargar_tabla()
        except Exception as e:
            self.lbl_msg.configure(
                text=f"❌  {e}", text_color="#E24B4A")