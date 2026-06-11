import customtkinter as ctk
from database.conexion import get_connection

class RecorridoVisitanteView:
    def __init__(self, parent):
        self.parent     = parent
        self.recorridos = []
        self.visitantes = []
        self.build()
        self.cargar_tabla()

    def build(self):
        ctk.CTkLabel(self.parent, text="🎟️  Inscripción a Recorridos",
                     font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(16,2), anchor="w", padx=24)
        ctk.CTkLabel(self.parent,
                     text="Anotá visitantes a los recorridos del parque",
                     text_color="gray", font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=24, pady=(0,12))

        contenedor = ctk.CTkFrame(self.parent, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=16)

        # ── Tabla ─────────────────────────────────────────
        frame_tabla = ctk.CTkFrame(contenedor)
        frame_tabla.pack(side="left", fill="both", expand=True, padx=(0,8))

        ctk.CTkLabel(frame_tabla, text="Inscripciones registradas",
                     font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(12,6), padx=12, anchor="w")

        self.scroll = ctk.CTkScrollableFrame(frame_tabla, height=400)
        self.scroll.pack(fill="both", expand=True, padx=8, pady=(0,8))

        for i, col in enumerate(["Visitante", "DNI", "Recorrido", "Horario"]):
            ctk.CTkLabel(self.scroll, text=col,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="gray"
            ).grid(row=0, column=i, padx=10, pady=4, sticky="w")

        self.filas = []

        # ── Formulario ────────────────────────────────────
        frame_form = ctk.CTkFrame(contenedor, width=320)
        frame_form.pack(side="right", fill="y")
        frame_form.pack_propagate(False)

        ctk.CTkLabel(frame_form, text="Anotar visitante",
                     font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(20,6), padx=14)

        ctk.CTkLabel(frame_form, text="Visitante",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(10,0))
        self.cb_visitante = ctk.CTkComboBox(frame_form, width=280, values=[])
        self.cb_visitante.pack(padx=14)

        ctk.CTkLabel(frame_form, text="Recorrido",
                     font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=14, pady=(10,0))
        self.cb_recorrido = ctk.CTkComboBox(frame_form, width=280, values=[])
        self.cb_recorrido.pack(padx=14)

        # Info del recorrido seleccionado
        self.lbl_info = ctk.CTkLabel(frame_form, text="",
                                     font=ctk.CTkFont(size=11),
                                     text_color="gray")
        self.lbl_info.pack(pady=(6,0), padx=14, anchor="w")

        self.cb_recorrido.configure(command=self.mostrar_info)

        ctk.CTkButton(frame_form, text="✅  Inscribir visitante",
                      command=self.guardar, height=42,
                      font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=20, padx=14, fill="x")

        self.lbl_msg = ctk.CTkLabel(frame_form, text="",
                                    font=ctk.CTkFont(size=12))
        self.lbl_msg.pack()

        self.cargar_combos()

    def cargar_combos(self):
        try:
            conn = get_connection()
            cur  = conn.cursor()

            cur.execute("""
                SELECT DNI, nombre + ' ' + apellido AS fullname
                FROM   Visitante
                ORDER  BY apellido
            """)
            self.visitantes = cur.fetchall()
            self.cb_visitante.configure(
                values=[v.fullname for v in self.visitantes])
            if self.visitantes:
                self.cb_visitante.set(self.visitantes[0].fullname)

            cur.execute("""
                SELECT r.codRecorrido, r.nombre, r.horario,
                       r.duracion, v.modelo
                FROM   Recorrido      r
                JOIN   VehiculoSafari v ON r.vehiculoSafari = v.codVehiculo
                ORDER  BY r.horario
            """)
            self.recorridos = cur.fetchall()
            self.cb_recorrido.configure(
                values=[r.nombre for r in self.recorridos])
            if self.recorridos:
                self.cb_recorrido.set(self.recorridos[0].nombre)
                self.mostrar_info(self.recorridos[0].nombre)

            conn.close()
        except Exception as ex:
            self.lbl_msg.configure(text=f"Error: {ex}",
                                   text_color="#E24B4A")

    def mostrar_info(self, nombre_seleccionado):
        try:
            rec = next(r for r in self.recorridos
                       if r.nombre == nombre_seleccionado)
            self.lbl_info.configure(
                text=f"🕐 {str(rec.horario)[:5]}  ·  "
                     f"⏱ {rec.duracion} min  ·  "
                     f"🚗 {rec.modelo}"
            )
        except:
            pass

    def cargar_tabla(self):
        for ws in self.filas:
            for w in ws: w.destroy()
        self.filas = []
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT vi.nombre + ' ' + vi.apellido AS visitante,
                       vi.DNI,
                       r.nombre  AS recorrido,
                       r.horario
                FROM   Recorrido_Visitante rv
                JOIN   Visitante  vi ON rv.DNI_Visitante = vi.DNI
                JOIN   Recorrido  r  ON rv.codRecorrido  = r.codRecorrido
                ORDER  BY r.horario, vi.apellido
            """)
            for row, fila in enumerate(cur.fetchall(), 1):
                ws = []
                for col, val in enumerate([
                    fila.visitante, str(fila.DNI),
                    fila.recorrido, str(fila.horario)[:5]
                ]):
                    lbl = ctk.CTkLabel(self.scroll, text=val,
                                       font=ctk.CTkFont(size=12))
                    lbl.grid(row=row, column=col,
                             padx=10, pady=3, sticky="w")
                    ws.append(lbl)
                self.filas.append(ws)
            conn.close()
        except Exception as ex:
            self.lbl_msg.configure(text=f"Error: {ex}",
                                   text_color="#E24B4A")

    def guardar(self):
        visitante_n  = self.cb_visitante.get()
        recorrido_n  = self.cb_recorrido.get()

        try:
            dni = next(v.DNI for v in self.visitantes
                       if v.fullname == visitante_n)
            cod = next(r.codRecorrido for r in self.recorridos
                       if r.nombre == recorrido_n)

            conn = get_connection()
            cur  = conn.cursor()

            # Verificar que no esté ya inscripto
            cur.execute("""
                SELECT COUNT(*) FROM Recorrido_Visitante
                WHERE codRecorrido = ? AND DNI_Visitante = ?
            """, (cod, dni))
            if cur.fetchone()[0] > 0:
                self.lbl_msg.configure(
                    text="⚠️  Este visitante ya está inscripto",
                    text_color="orange")
                conn.close()
                return

            cur.execute("""
                INSERT INTO Recorrido_Visitante
                    (codRecorrido, DNI_Visitante)
                VALUES (?, ?)
            """, (cod, dni))
            conn.commit()
            conn.close()

            self.lbl_msg.configure(
                text="✅  Inscripción registrada correctamente",
                text_color="#1D9E75")
            self.cargar_tabla()

        except Exception as ex:
            self.lbl_msg.configure(text=f"❌  {ex}",
                                   text_color="#E24B4A")