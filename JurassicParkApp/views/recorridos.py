import customtkinter as ctk
from database.conexion import get_connection

class RecorridosView:
    def __init__(self, parent):
        self.parent   = parent
        self.vehiculos = []
        self.build()
        self.cargar_tabla()

    def build(self):
        ctk.CTkLabel(self.parent, text="🚗  Recorridos",
                     font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(16,2), anchor="w", padx=24)
        ctk.CTkLabel(self.parent, text="Tours y recorridos disponibles",
                     text_color="gray", font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=24, pady=(0,12))

        contenedor = ctk.CTkFrame(self.parent, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=16)

        # ── Tabla ─────────────────────────────────────────
        frame_tabla = ctk.CTkFrame(contenedor)
        frame_tabla.pack(side="left", fill="both", expand=True, padx=(0,8))

        self.scroll = ctk.CTkScrollableFrame(frame_tabla, height=400)
        self.scroll.pack(fill="both", expand=True, padx=8, pady=8)

        for i, col in enumerate(["Nombre","Duración (min)",
                                  "Horario","Vehículo"]):
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

        ctk.CTkLabel(frame_form, text="Registrar recorrido",
                     font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(14,10))

        ctk.CTkLabel(frame_form, text="Nombre",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.tf_nombre = ctk.CTkEntry(frame_form, width=265,
                                      placeholder_text="Ej: Tour Nocturno")
        self.tf_nombre.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Duración (minutos)",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.tf_dur = ctk.CTkEntry(frame_form, width=265,
                                   placeholder_text="Ej: 60")
        self.tf_dur.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Horario (HH:MM)",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.tf_horario = ctk.CTkEntry(frame_form, width=265,
                                       placeholder_text="Ej: 16:00")
        self.tf_horario.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Vehículo",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(6,0))
        self.cb_vehiculo = ctk.CTkComboBox(frame_form, width=265, values=[])
        self.cb_vehiculo.pack(padx=14)

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
            cur.execute("""
                SELECT codVehiculo, modelo
                FROM   VehiculoSafari
                WHERE  estado = 'Disponible'
                ORDER  BY modelo
            """)
            self.vehiculos = cur.fetchall()
            self.cb_vehiculo.configure(
                values=[v.modelo for v in self.vehiculos])
            if self.vehiculos:
                self.cb_vehiculo.set(self.vehiculos[0].modelo)
            conn.close()
        except Exception as ex:
            self.lbl_msg.configure(text=f"Error combos: {ex}",
                                   text_color="orange")

    def cargar_tabla(self):
        for ws in self.filas:
            for w in ws: w.destroy()
        self.filas    = []
        self.ids_fila = []
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT r.codRecorrido, r.nombre, r.duracion,
                       r.horario, v.modelo
                FROM   Recorrido      r
                JOIN   VehiculoSafari v ON r.vehiculoSafari = v.codVehiculo
                ORDER  BY r.horario
            """)
            for r, fila in enumerate(cur.fetchall(), 1):
                self.ids_fila.append(fila.codRecorrido)
                vals = [fila.nombre, str(fila.duracion),
                        str(fila.horario)[:5], fila.modelo]
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
        nombre  = self.tf_nombre.get().strip()
        dur     = self.tf_dur.get().strip()
        horario = self.tf_horario.get().strip()
        veh_n   = self.cb_vehiculo.get()

        if not all([nombre, dur, horario]):
            self.lbl_msg.configure(
                text="⚠️  Completá todos los campos", text_color="orange")
            return
        try:
            cod_veh = next(v.codVehiculo for v in self.vehiculos
                           if v.modelo == veh_n)
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO Recorrido
                    (nombre, duracion, horario, vehiculoSafari)
                VALUES (?, ?, ?, ?)
            """, (nombre, int(dur), horario, cod_veh))
            conn.commit()
            conn.close()
            self.lbl_msg.configure(text="✅  Guardado correctamente",
                                   text_color="#1D9E75")
            self.tf_nombre.delete(0, "end")
            self.tf_dur.delete(0, "end")
            self.tf_horario.delete(0, "end")
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
                "DELETE FROM Recorrido WHERE codRecorrido = ?", (cod,))
            conn.commit()
            conn.close()
            self.lbl_msg.configure(text="🗑  Eliminado",
                                   text_color="#1D9E75")
            self.seleccionado = None
            self.cargar_tabla()
        except Exception as ex:
            self.lbl_msg.configure(text=f"❌  {ex}",
                                   text_color="#E24B4A")