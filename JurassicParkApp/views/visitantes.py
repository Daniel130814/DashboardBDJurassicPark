import customtkinter as ctk
from database.conexion import get_connection

class VisitantesView:
    def __init__(self, parent):
        self.parent = parent
        self.build()
        self.cargar_tabla()

    def build(self):
        ctk.CTkLabel(self.parent, text="🎟️  Visitantes",
                     font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(16,2), anchor="w", padx=24)

        contenedor = ctk.CTkFrame(self.parent, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=16)

        # Tabla
        frame_tabla = ctk.CTkFrame(contenedor)
        frame_tabla.pack(side="left", fill="both", expand=True, padx=(0,8))

        self.scroll = ctk.CTkScrollableFrame(frame_tabla, height=420)
        self.scroll.pack(fill="both", expand=True, padx=8, pady=8)

        for i, col in enumerate(["DNI","Nombre","Apellido","Email","Teléfono"]):
            ctk.CTkLabel(self.scroll, text=col,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="gray"
            ).grid(row=0, column=i, padx=8, pady=4, sticky="w")
        self.filas = []

        # Formulario
        frame_form = ctk.CTkFrame(contenedor, width=300)
        frame_form.pack(side="right", fill="y")
        frame_form.pack_propagate(False)

        ctk.CTkLabel(frame_form, text="Registrar visitante",
                     font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(14,10))

        self.campos = {}
        for label, ph in [("DNI","Ej: 40000011"),
                           ("Nombre","Ej: Alan"),
                           ("Apellido","Ej: Grant"),
                           ("Email","Ej: alan@jurassic.com"),
                           ("Teléfono","Ej: 555-9999")]:
            ctk.CTkLabel(frame_form, text=label,
                         font=ctk.CTkFont(size=12)
            ).pack(anchor="w", padx=14, pady=(6,0))
            e = ctk.CTkEntry(frame_form, width=260,
                             placeholder_text=ph)
            e.pack(padx=14)
            self.campos[label] = e

        ctk.CTkButton(frame_form, text="💾  Guardar",
                      command=self.guardar, height=38
        ).pack(pady=14, padx=14, fill="x")

        self.lbl_msg = ctk.CTkLabel(frame_form, text="")
        self.lbl_msg.pack()

    def cargar_tabla(self):
        for ws in self.filas:
            for w in ws: w.destroy()
        self.filas = []
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute(
                "SELECT DNI,nombre,apellido,email,telefono FROM Visitante")
            for r, fila in enumerate(cur.fetchall(), 1):
                ws = []
                for c, val in enumerate([str(fila.DNI), fila.nombre,
                                          fila.apellido, fila.email,
                                          fila.telefono]):
                    lbl = ctk.CTkLabel(self.scroll, text=val,
                                       font=ctk.CTkFont(size=12))
                    lbl.grid(row=r, column=c, padx=8, pady=3, sticky="w")
                    ws.append(lbl)
                self.filas.append(ws)
            conn.close()
        except Exception as e:
            self.lbl_msg.configure(text=f"Error: {e}",
                                   text_color="#E24B4A")

    def guardar(self):
        vals = {k: v.get().strip() for k, v in self.campos.items()}
        if not all(vals.values()):
            self.lbl_msg.configure(
                text="⚠️  Completá todos los campos", text_color="orange")
            return
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute(
                "INSERT INTO Visitante (DNI,nombre,apellido,email,telefono) "
                "VALUES (?,?,?,?,?)",
                (int(vals["DNI"]), vals["Nombre"], vals["Apellido"],
                 vals["Email"], vals["Teléfono"]))
            conn.commit()
            conn.close()
            self.lbl_msg.configure(
                text="✅  Guardado", text_color="#1D9E75")
            for e in self.campos.values(): e.delete(0,"end")
            self.cargar_tabla()
        except Exception as e:
            self.lbl_msg.configure(
                text=f"❌  {e}", text_color="#E24B4A")