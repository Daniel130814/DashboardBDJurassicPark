import customtkinter as ctk
from database.conexion import get_connection

class CuidadoresView:
    def __init__(self, parent):
        self.parent = parent
        self.build()
        self.cargar_tabla()

    def build(self):
        ctk.CTkLabel(self.parent, text="👷  Cuidadores",
                     font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(16,2), anchor="w", padx=24)
        ctk.CTkLabel(self.parent, text="Gestioná el personal de cuidado del parque",
                     text_color="gray", font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=24, pady=(0,12))

        contenedor = ctk.CTkFrame(self.parent, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=16)

        # ── Tabla ─────────────────────────────────────────
        frame_tabla = ctk.CTkFrame(contenedor)
        frame_tabla.pack(side="left", fill="both", expand=True, padx=(0,8))

        ctk.CTkLabel(frame_tabla, text="Cuidadores registrados",
                     font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(12,6), padx=12, anchor="w")

        self.scroll = ctk.CTkScrollableFrame(frame_tabla, height=400)
        self.scroll.pack(fill="both", expand=True, padx=8, pady=(0,8))

        for i, col in enumerate(["Legajo","Nombre","Apellido",
                                  "Teléfono","Fecha Ingreso"]):
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

        ctk.CTkLabel(frame_form, text="Registrar cuidador",
                     font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(14,10))

        self.campos = {}
        for label, ph in [
            ("Legajo",          "Ej: 1006"),
            ("Nombre",          "Ej: Alan"),
            ("Apellido",        "Ej: Grant"),
            ("Teléfono",        "Ej: 555-0110"),
            ("Fecha Ingreso",   "YYYY-MM-DD"),
        ]:
            ctk.CTkLabel(frame_form, text=label,
                         font=ctk.CTkFont(size=12)
            ).pack(anchor="w", padx=14, pady=(6,0))
            e = ctk.CTkEntry(frame_form, width=265,
                             placeholder_text=ph)
            e.pack(padx=14)
            self.campos[label] = e

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
                SELECT LegajoCuidador, nombre, apellido,
                       telefono, fechaIngreso
                FROM   Cuidador
                ORDER  BY apellido
            """)
            for r, fila in enumerate(cur.fetchall(), 1):
                self.ids_fila.append(fila.LegajoCuidador)
                vals = [str(fila.LegajoCuidador), fila.nombre,
                        fila.apellido, fila.telefono,
                        str(fila.fechaIngreso)[:10]]
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
        vals = {k: v.get().strip() for k, v in self.campos.items()}
        if not all(vals.values()):
            self.lbl_msg.configure(
                text="⚠️  Completá todos los campos", text_color="orange")
            return
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO Cuidador
                    (LegajoCuidador, nombre, apellido, telefono, fechaIngreso)
                VALUES (?, ?, ?, ?, ?)
            """, (int(vals["Legajo"]), vals["Nombre"], vals["Apellido"],
                  vals["Teléfono"], vals["Fecha Ingreso"]))
            conn.commit()
            conn.close()
            self.lbl_msg.configure(text="✅  Guardado correctamente",
                                   text_color="#1D9E75")
            for e in self.campos.values(): e.delete(0, "end")
            self.cargar_tabla()
        except Exception as ex:
            self.lbl_msg.configure(text=f"❌  {ex}",
                                   text_color="#E24B4A")

    def eliminar(self):
        if self.seleccionado is None:
            self.lbl_msg.configure(
                text="⚠️  Seleccioná una fila primero", text_color="orange")
            return
        legajo = self.ids_fila[self.seleccionado]
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute(
                "DELETE FROM Cuidador WHERE LegajoCuidador = ?", (legajo,))
            conn.commit()
            conn.close()
            self.lbl_msg.configure(text="🗑  Eliminado",
                                   text_color="#1D9E75")
            self.seleccionado = None
            self.cargar_tabla()
        except Exception as ex:
            self.lbl_msg.configure(text=f"❌  {ex}",
                                   text_color="#E24B4A")