import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
DB_NAME = "gestion_academica.db"
def conexion_bd():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
def configurar_base_datos():
    with conexion_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                usuario TEXT PRIMARY KEY,
                contrasena TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL 
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departamentos (
                id_depa INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL UNIQUE
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS municipios (
                id_muni INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                id_depa INTEGER,
                FOREIGN KEY(id_depa) REFERENCES departamentos(id_depa)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carreras (
                id_carrera INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL UNIQUE,
                costo_mensualidad REAL NOT NULL 
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estudiantes (
                carne TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                dpi TEXT UNIQUE,
                edad INTEGER,
                id_carrera INTEGER,
                id_depa INTEGER,
                id_muni INTEGER,
                saldo_favor_mensualidad REAL DEFAULT 0.0,
                saldo_favor_otros REAL DEFAULT 0.0,
                FOREIGN KEY(id_carrera) REFERENCES carreras(id_carrera),
                FOREIGN KEY(id_depa) REFERENCES departamentos(id_depa),
                FOREIGN KEY(id_muni) REFERENCES municipios(id_muni)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS secretarias (
                id_secretaria INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                dpi TEXT UNIQUE,
                edad INTEGER
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tipos_pagos (
                id_tipo_pago INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL UNIQUE,
                monto_fijo REAL, 
                es_mensualidad INTEGER NOT NULL DEFAULT 0 
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS boletas (
                no_boleta TEXT PRIMARY KEY,
                fecha_realizacion TEXT NOT NULL,
                monto_depositado REAL NOT NULL,
                banco TEXT NOT NULL, 
                carne_estudiante TEXT,
                acreditada INTEGER DEFAULT 0, 
                fecha_acreditacion TEXT,
                secretaria_id INTEGER,
                FOREIGN KEY(carne_estudiante) REFERENCES estudiantes(carne),
                FOREIGN KEY(secretaria_id) REFERENCES secretarias(id_secretaria)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pagos_boleta (
                id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                no_boleta TEXT,
                id_tipo_pago INTEGER,
                monto_aplicado REAL NOT NULL,
                descripcion TEXT,
                FOREIGN KEY(no_boleta) REFERENCES boletas(no_boleta),
                FOREIGN KEY(id_tipo_pago) REFERENCES tipos_pagos(id_tipo_pago)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS banco (
                id_deposito INTEGER PRIMARY KEY AUTOINCREMENT,
                no_boleta TEXT UNIQUE,
                monto REAL NOT NULL,
                fecha_deposito TEXT NOT NULL,
                FOREIGN KEY(no_boleta) REFERENCES boletas(no_boleta)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registro_actividades (
                id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL,
                actividad TEXT NOT NULL,
                usuario_responsable TEXT
            );
        """)
        conn.commit()
    insertar_datos_iniciales()
def insertar_datos_iniciales():
    with conexion_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM carreras")
        if cursor.fetchone()[0] == 0:
            carreras = [
                ("Ingeniería en Sistemas", 650.00),
                ("Licenciatura en Administración", 550.00),
                ("Medicina", 800.00)
            ]
            conn.executemany("INSERT INTO carreras (nombre, costo_mensualidad) VALUES (?, ?)", carreras)
        cursor.execute("SELECT COUNT(*) FROM tipos_pagos")
        if cursor.fetchone()[0] == 0:
            tipos_pagos = [
                ("Mensualidad", 0.0, 1),
                ("Examen de Recuperación", 150.00, 0),
                ("Matrícula", 200.00, 0),
                ("Curso de Verano", 300.00, 0)
            ]
            conn.executemany("INSERT INTO tipos_pagos (nombre, monto_fijo, es_mensualidad) VALUES (?, ?, ?)",
                             tipos_pagos)
        cursor.execute("SELECT COUNT(*) FROM departamentos")
        if cursor.fetchone()[0] == 0:
            depas = [(1, "Guatemala"), (2, "Quetzaltenango")]
            conn.executemany("INSERT INTO departamentos (id_depa, nombre) VALUES (?, ?)", depas)
            munis = [("Guatemala", 1), ("Mixco", 1), ("Quetzaltenango", 2), ("Coatepeque", 2)]
            conn.executemany("INSERT INTO municipios (nombre, id_depa) VALUES (?, ?)", munis)
        cursor.execute("SELECT COUNT(*) FROM secretarias")
        if cursor.fetchone()[0] == 0:
            conn.execute("INSERT INTO secretarias (nombre, apellido, dpi, edad) VALUES (?, ?, ?, ?)",
                         ("Ana", "García", "1234567890101", 30))
            conn.execute("INSERT OR REPLACE INTO usuarios (usuario, contrasena, tipo_usuario) VALUES (?, ?, ?)",
                         ("ana.secretaria", "123", "SECRETARIA"))
        cursor.execute("SELECT COUNT(*) FROM estudiantes")
        if cursor.fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO estudiantes (carne, nombre, apellido, dpi, edad, id_carrera, id_depa, id_muni) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ("20240001", "Pedro", "López", "1098765432101", 20, 1, 1, 1))
            conn.execute("INSERT OR REPLACE INTO usuarios (usuario, contrasena, tipo_usuario) VALUES (?, ?, ?)",
                         ("20240001", "123", "ESTUDIANTE"))
        conn.commit()
class Usuario:
    def __init__(self, usuario, contrasena, tipo_usuario):
        self.usuario = usuario
        self.contrasena = contrasena
        self.tipo_usuario = tipo_usuario
    @staticmethod
    def validar_credenciales(usuario, contrasena):
        with conexion_bd() as conn:
            cursor = conn.execute("SELECT tipo_usuario FROM usuarios WHERE usuario = ? AND contrasena = ?",
                                  (usuario, contrasena))
            row = cursor.fetchone()
            if row:
                return row['tipo_usuario']
            return None
class Estudiante:
    def __init__(self, carne, nombre, apellido, dpi, edad, id_carrera, id_depa, id_muni):
        self.carne = carne
        self.nombre = nombre
        self.apellido = apellido
        self.dpi = dpi
        self.edad = edad
        self.id_carrera = id_carrera
        self.id_depa = id_depa
        self.id_muni = id_muni
    def guardar(self, contrasena):
        with conexion_bd() as conn:
            try:
                conn.execute(
                    "INSERT INTO estudiantes (carne, nombre, apellido, dpi, edad, id_carrera, id_depa, id_muni) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (self.carne, self.nombre, self.apellido, self.dpi, self.edad, self.id_carrera, self.id_depa,
                     self.id_muni)
                )
            except sqlite3.IntegrityError:
                return False
            conn.execute(
                "INSERT INTO usuarios (usuario, contrasena, tipo_usuario) VALUES (?, ?, ?)",
                (self.carne, contrasena, "ESTUDIANTE")
            )
            conn.commit()
            Registro.registrar_actividad("SECRETARIA", f"Estudiante {self.carne} inscrito.")
            return True
    @staticmethod
    def obtener_info(carne):
        with conexion_bd() as conn:
            query = """
                SELECT 
                    e.*, c.nombre AS carrera_nombre, d.nombre AS depa_nombre, m.nombre AS muni_nombre
                FROM estudiantes e
                JOIN carreras c ON e.id_carrera = c.id_carrera
                JOIN departamentos d ON e.id_depa = d.id_depa
                JOIN municipios m ON e.id_muni = m.id_muni
                WHERE e.carne = ?
            """
            cursor = conn.execute(query, (carne,))
            return cursor.fetchone()
    @staticmethod
    def actualizar_saldo(carne, tipo_pago_es_mensualidad, monto):
        with conexion_bd() as conn:
            columna = 'saldo_favor_mensualidad' if tipo_pago_es_mensualidad else 'saldo_favor_otros'
            conn.execute(f"UPDATE estudiantes SET {columna} = {columna} + ? WHERE carne = ?", (monto, carne))
            conn.commit()
    @staticmethod
    def usar_saldo(carne, es_mensualidad, monto_a_usar):
        with conexion_bd() as conn:
            columna = 'saldo_favor_mensualidad' if es_mensualidad else 'saldo_favor_otros'
            conn.execute(f"UPDATE estudiantes SET {columna} = {columna} - ? WHERE carne = ?", (monto_a_usar, carne))
            conn.commit()
class Secretaria:
    @staticmethod
    def obtener_id_por_usuario(usuario):
        with conexion_bd() as conn:
            cursor = conn.execute(
                "SELECT id_secretaria FROM secretarias WHERE rowid = (SELECT rowid FROM usuarios WHERE usuario = ?)",
                (usuario,))
            row = cursor.fetchone()
            return row['id_secretaria'] if row else None
class Boleta:
    def __init__(self, no_boleta, fecha_realizacion, monto_depositado, banco, carne_estudiante):
        self.no_boleta = no_boleta
        self.fecha_realizacion = fecha_realizacion
        self.monto_depositado = monto_depositado
        self.banco = banco
        self.carne_estudiante = carne_estudiante
    def guardar_con_pago_en_banco(self):
        with conexion_bd() as conn:
            try:
                conn.execute(
                    "INSERT INTO boletas (no_boleta, fecha_realizacion, monto_depositado, banco, carne_estudiante) VALUES (?, ?, ?, ?, ?)",
                    (self.no_boleta, self.fecha_realizacion, self.monto_depositado, self.banco, self.carne_estudiante)
                )
            except sqlite3.IntegrityError:
                return False
            conn.execute(
                "INSERT INTO banco (no_boleta, monto, fecha_deposito) VALUES (?, ?, ?)",
                (self.no_boleta, self.monto_depositado, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            Registro.registrar_actividad(self.carne_estudiante,
            f"Boleta {self.no_boleta} registrada para acreditación.")
            return True
    @staticmethod
    def listar_pendientes():
        with conexion_bd() as conn:
            query = """
                SELECT b.no_boleta, b.fecha_realizacion, b.monto_depositado, b.banco, e.carne, e.nombre, e.apellido
                FROM boletas b
                JOIN estudiantes e ON b.carne_estudiante = e.carne
                WHERE b.acreditada = 0
            """
            cursor = conn.execute(query)
            return cursor.fetchall()
    @staticmethod
    def listar_acreditadas(carne):
        with conexion_bd() as conn:
            query = """
                SELECT b.no_boleta, b.fecha_realizacion, b.monto_depositado, b.banco, b.fecha_acreditacion,
                       s.nombre AS secretaria_nombre, s.apellido AS secretaria_apellido
                FROM boletas b
                LEFT JOIN secretarias s ON b.secretaria_id = s.id_secretaria
                WHERE b.acreditada = 1 AND b.carne_estudiante = ?
                ORDER BY b.fecha_acreditacion DESC
            """
            cursor = conn.execute(query, (carne,))
            return cursor.fetchall()
    @staticmethod
    def obtener_info_boleta(no_boleta):
        with conexion_bd() as conn:
            query = """
                SELECT b.*, e.carne, e.nombre AS est_nombre, e.apellido AS est_apellido, e.id_carrera
                FROM boletas b
                JOIN estudiantes e ON b.carne_estudiante = e.carne
                WHERE b.no_boleta = ? AND b.acreditada = 0
            """
            cursor = conn.execute(query, (no_boleta,))
            return cursor.fetchone()

    @staticmethod
    def acreditar(no_boleta, secretaria_id):
        try:
            with conexion_bd() as conn:
                conn.execute(
                    "UPDATE boletas SET acreditada = 1, fecha_acreditacion = ?, secretaria_id = ? WHERE no_boleta = ?",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), secretaria_id, no_boleta)
                )
                conn.commit()
                Registro.registrar_actividad(f"SecID:{secretaria_id}",f"Boleta {no_boleta} acreditada y pagos aplicados.")
                return True
        except sqlite3.Error as e:
            print(f"Error DB al acreditar boleta {no_boleta}: {e}")
            return False
class TipoPago:
    @staticmethod
    def obtener_todo():
        with conexion_bd() as conn:
            cursor = conn.execute("SELECT * FROM tipos_pagos")
            return cursor.fetchall()
class PagosBoleta:
    @staticmethod
    def guardar_pago(no_boleta, id_tipo_pago, monto_aplicado, descripcion):
        with conexion_bd() as conn:
            conn.execute(
                "INSERT INTO pagos_boleta (no_boleta, id_tipo_pago, monto_aplicado, descripcion) VALUES (?, ?, ?, ?)",
                (no_boleta, id_tipo_pago, monto_aplicado, descripcion)
            )
            conn.commit()
    @staticmethod
    def obtener_pagos_por_estudiante(carne):
        with conexion_bd() as conn:
            query = """
                SELECT pb.no_boleta, tp.nombre AS tipo_pago, pb.monto_aplicado, pb.descripcion, b.fecha_acreditacion
                FROM pagos_boleta pb
                JOIN boletas b ON pb.no_boleta = b.no_boleta
                JOIN tipos_pagos tp ON pb.id_tipo_pago = tp.id_tipo_pago
                WHERE b.carne_estudiante = ? AND b.acreditada = 1
                ORDER BY b.fecha_acreditacion DESC
            """
            cursor = conn.execute(query, (carne,))
            return cursor.fetchall()
class Registro:
    @staticmethod
    def registrar_actividad(usuario_responsable, actividad):
        with conexion_bd() as conn:
            conn.execute(
                "INSERT INTO registro_actividades (fecha_hora, actividad, usuario_responsable) VALUES (?, ?, ?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), actividad, usuario_responsable)
            )
            conn.commit()
    @staticmethod
    def listar_registros():
        with conexion_bd() as conn:
            cursor = conn.execute("SELECT * FROM registro_actividades ORDER BY fecha_hora DESC")
            return cursor.fetchall()
class Carrera:
    @staticmethod
    def obtener_todo():
        with conexion_bd() as conn:
            return conn.execute("SELECT id_carrera, nombre FROM carreras").fetchall()
    @staticmethod
    def obtener_costo_mensualidad(id_carrera):
        with conexion_bd() as conn:
            cursor = conn.execute("SELECT costo_mensualidad FROM carreras WHERE id_carrera = ?", (id_carrera,))
            row = cursor.fetchone()
            return row['costo_mensualidad'] if row else 0.0
class Departamento:
    @staticmethod
    def obtener_todo():
        with conexion_bd() as conn:
            return conn.execute("SELECT id_depa, nombre FROM departamentos").fetchall()
class Municipio:
    @staticmethod
    def obtener_por_depa(id_depa):
        with conexion_bd() as conn:
            return conn.execute("SELECT id_muni, nombre FROM municipios WHERE id_depa = ?", (id_depa,)).fetchall()
class VentanaLogin(tk.Toplevel):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.title("Login al Sistema")
        self.geometry("300x200")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        self.transient(master)
        self.grab_set()
        style = ttk.Style(self)
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        frame = ttk.Frame(self, padding="15")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(frame, text="Usuario:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_usuario = ttk.Entry(frame, width=20)
        self.entry_usuario.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_contrasena = ttk.Entry(frame, show="*", width=20)
        self.entry_contrasena.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Ingresar", command=self.intentar_login).grid(row=2, column=0, columnspan=2, pady=10)
        self.entry_contrasena.bind('<Return>', lambda event: self.intentar_login())
        self.entry_usuario.focus_set()
    def intentar_login(self):
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contrasena.get()
        tipo_usuario = Usuario.validar_credenciales(usuario, contrasena)
        if tipo_usuario:
            self.destroy()
            messagebox.showinfo("Éxito", f"¡Bienvenido, {tipo_usuario.lower()}!")
            self.app.mostrar_menu_principal(tipo_usuario, usuario)
        else:
            messagebox.showerror("Error de Login", "Credenciales inválidas. Intente nuevamente.")
            self.entry_contrasena.delete(0, tk.END)
class VentanaMenuEstudiante(tk.Toplevel):
    def __init__(self, master, app_instance, carne_usuario):
        super().__init__(master)
        self.app = app_instance
        self.carne = carne_usuario
        self.title(f"Menú Estudiante - {self.carne}")
        self.geometry("500x350")
        self.transient(master)
        self.grab_set()
        tk.Label(self, text=f"Bienvenido Estudiante: {self.carne}", font=('Arial', 14, 'bold')).pack(pady=10)
        botones = [
            ("Ingresar nueva boleta de pago", self.mostrar_ingresar_boleta),
            ("Ver boletas acreditadas y pagos", self.ver_pagos_ui),
            ("Ver saldos a favor", self.ver_saldos_ui),
            ("Cerrar Sesión", self.cerrar_sesion)
        ]
        for texto, comando in botones:
            ttk.Button(self, text=texto, command=comando).pack(pady=5, padx=20, fill='x')
    def mostrar_ingresar_boleta(self):
        VentanaIngresarBoleta(self.master, self.carne)
    def ver_pagos_ui(self):
        VentanaHistorialPagosEstudiante(self.master, self.carne)
    def ver_saldos_ui(self):
        VentanaVerSaldos(self.master, self.carne)
    def cerrar_sesion(self):
        self.destroy()
        self.app.volver_a_login()
class VentanaMenuSecretaria(tk.Toplevel):
    def __init__(self, master, app_instance, usuario_secretaria):
        super().__init__(master)
        self.app = app_instance
        self.usuario = usuario_secretaria
        self.title(f"Menú Secretaria - {self.usuario}")
        self.geometry("500x400")
        self.transient(master)
        self.grab_set()
        tk.Label(self, text=f"Bienvenida Secretaria: {self.usuario}", font=('Arial', 14, 'bold')).pack(pady=10)
        botones = [
            ("Inscribir nuevo estudiante", self.inscribir_estudiante_ui),
            ("Acreditar boletas pendientes", self.acreditar_boletas_ui),
            ("Ver registros de pagos (por carné)", self.ver_pagos_por_carne_ui),
            ("Cerrar Sesión", self.cerrar_sesion)
        ]
        for texto, comando in botones:
            ttk.Button(self, text=texto, command=comando).pack(pady=5, padx=20, fill='x')
    def inscribir_estudiante_ui(self):
        VentanaInscribirEstudiante(self.master, self.app)
    def acreditar_boletas_ui(self):
        secretaria_id = Secretaria.obtener_id_por_usuario(self.usuario)
        if secretaria_id:
            VentanaAcreditarBoletas(self.master, self.app, secretaria_id)
        else:
            messagebox.showerror("Error", "No se pudo obtener el ID de la secretaria.")
    def ver_pagos_por_carne_ui(self):
        VentanaConsultaPagosSecretaria(self.master)
    def cerrar_sesion(self):
        self.destroy()
        self.app.volver_a_login()
class VentanaIngresarBoleta(tk.Toplevel):
    def __init__(self, master, carne_estudiante):
        super().__init__(master)
        self.carne = carne_estudiante
        self.title(f"Ingresar Boleta para {self.carne}")
        self.geometry("450x400")
        self.transient(master)
        self.grab_set()
        self.tipos_pagos_db = TipoPago.obtener_todo()
        self.opciones_pagos = [f"{tp['id_tipo_pago']}. {tp['nombre']}" for tp in self.tipos_pagos_db]
        self.opciones_pagos.append("0. Múltiples Pagos")
        tk.Label(self, text="Registro de Nueva Boleta de Pago", font=('Arial', 14, 'bold')).pack(pady=10)
        frame = ttk.Frame(self, padding="10")
        frame.pack(padx=10, pady=5, fill='x')
        ttk.Label(frame, text="* No. Boleta:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_no_boleta = ttk.Entry(frame, width=30)
        self.entry_no_boleta.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(frame, text="* Fecha (AAAA-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_fecha = ttk.Entry(frame, width=30)
        self.entry_fecha.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ttk.Label(frame, text="* Monto Depositado (Q):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_monto = ttk.Entry(frame, width=30)
        self.entry_monto.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(frame, text="* Banco:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.bancos = ["Banrural", "BI"]
        self.var_banco = tk.StringVar()
        self.combo_banco = ttk.Combobox(frame, textvariable=self.var_banco, values=self.bancos, state="readonly", width=28)
        self.combo_banco.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        if self.bancos: self.combo_banco.set(self.bancos[0])
        ttk.Label(frame, text="* Tipo de Pago:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.var_tipo_pago = tk.StringVar()
        self.combo_tipo_pago = ttk.Combobox(frame, textvariable=self.var_tipo_pago, values=self.opciones_pagos, state="readonly", width=28)
        self.combo_tipo_pago.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        if self.opciones_pagos: self.combo_tipo_pago.set(self.opciones_pagos[0])
        ttk.Label(frame, text="Descripción (si es Múltiple):").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.entry_descripcion = ttk.Entry(frame, width=30)
        self.entry_descripcion.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(self, text="Guardar Boleta", command=self.guardar_boleta).pack(pady=15)
    def guardar_boleta(self):
        no_boleta = self.entry_no_boleta.get().strip()
        fecha_realizacion = self.entry_fecha.get().strip()
        banco = self.var_banco.get()
        tipo_pago_seleccionado = self.var_tipo_pago.get()
        try:
            monto_depositado = float(self.entry_monto.get())
        except ValueError:
            messagebox.showerror("Error de Entrada", "El monto debe ser un número válido.")
            return
        if not all([no_boleta, fecha_realizacion, banco, tipo_pago_seleccionado, monto_depositado > 0]):
            messagebox.showerror("Error de Validación","Todos los campos obligatorios deben estar llenos y el monto debe ser positivo.")
            return
        id_pago_str = tipo_pago_seleccionado.split('.')[0]
        id_pago = id_pago_str if id_pago_str.isdigit() else '0'
        if id_pago == '0' and not self.entry_descripcion.get().strip():
            messagebox.showerror("Error de Validación", "Si selecciona 'Múltiples Pagos', debe añadir una descripción.")
            return
        boleta = Boleta(no_boleta, fecha_realizacion, monto_depositado, banco, self.carne)
        if boleta.guardar_con_pago_en_banco():
            if id_pago != '0':
                PagosBoleta.guardar_pago(
                    no_boleta,
                    int(id_pago),
                    monto_depositado,
                    f"Pago inicializado con boleta {no_boleta}"
                )
            else:
                PagosBoleta.guardar_pago(
                    no_boleta,
                    1,
                    monto_depositado,
                    self.entry_descripcion.get().strip()
                )
            messagebox.showinfo("Éxito", f"Boleta {no_boleta} registrada y enviada al banco para su verificación.")
            self.destroy()
        else:
            messagebox.showerror("Error al Guardar", "El número de boleta ya existe o hubo un error de integridad de datos.")
class VentanaHistorialPagosEstudiante(tk.Toplevel):
    def __init__(self, master, carne_estudiante):
        super().__init__(master)
        self.carne = carne_estudiante
        self.title(f"Historial de Pagos - {self.carne}")
        self.geometry("850x500")
        self.transient(master)
        self.grab_set()
        tk.Label(self, text=f"Historial de Transacciones del Estudiante {self.carne}", font=('Arial', 14, 'bold')).pack(
        pady=10)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill='both')
        frame_boletas = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame_boletas, text="Boletas Acreditadas")
        self.crear_tabla_boletas(frame_boletas)
        self.cargar_boletas()
        frame_pagos = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame_pagos, text="Pagos Aplicados")
        self.crear_tabla_pagos(frame_pagos)
        self.cargar_pagos()
    def crear_tabla_boletas(self, frame):
        self.tree_boletas = ttk.Treeview(frame,
        columns=("No_Boleta", "Monto", "Banco", "F_Realiz", "F_Acredit", "Secretaria"),
        show='headings')
        self.tree_boletas.heading("No_Boleta", text="No. Boleta")
        self.tree_boletas.heading("Monto", text="Monto (Q)")
        self.tree_boletas.heading("Banco", text="Banco")
        self.tree_boletas.heading("F_Realiz", text="F. Realización")
        self.tree_boletas.heading("F_Acredit", text="F. Acreditación")
        self.tree_boletas.heading("Secretaria", text="Secretaria")
        self.tree_boletas.column("No_Boleta", width= 100, anchor='center')
        self.tree_boletas.column("Monto", width= 100, anchor='e')
        self.tree_boletas.column("Banco", width= 100)
        self.tree_boletas.column("F_Realiz", width= 100, anchor='center')
        self.tree_boletas.column("F_Acredit", width= 120, anchor='center')
        self.tree_boletas.column("Secretaria", width= 200)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree_boletas.yview)
        vsb.pack(side='right', fill='y')
        self.tree_boletas.configure(yscrollcommand=vsb.set)
        self.tree_boletas.pack(fill='both', expand=True)
    def cargar_boletas(self):
        for item in self.tree_boletas.get_children():
            self.tree_boletas.delete(item)
        boletas = Boleta.listar_acreditadas(self.carne)
        for b in boletas:
            secretaria = f"{b['secretaria_nombre']} {b['secretaria_apellido']}" if b['secretaria_nombre'] else "N/A"
            self.tree_boletas.insert('', tk.END, values=(
                b['no_boleta'],
                f"{b['monto_depositado']:.2f}",
                b['banco'],
                b['fecha_realizacion'],
                b['fecha_acreditacion'],
                secretaria
            ))
    def crear_tabla_pagos(self, frame):
        self.tree_pagos = ttk.Treeview(frame, columns=("Tipo", "Monto", "Descripcion", "Boleta", "F_Acredit"),
        show='headings')
        self.tree_pagos.heading("Tipo", text="Tipo de Pago")
        self.tree_pagos.heading("Monto", text="Monto Aplicado (Q)")
        self.tree_pagos.heading("Descripcion", text="Descripción")
        self.tree_pagos.heading("Boleta", text="No. Boleta")
        self.tree_pagos.heading("F_Acredit", text="F. Acreditación")
        self.tree_pagos.column("Tipo", width=150)
        self.tree_pagos.column("Monto", width=120, anchor='e')
        self.tree_pagos.column("Descripcion", width=300)
        self.tree_pagos.column("Boleta", width=100, anchor='center')
        self.tree_pagos.column("F_Acredit", width=120, anchor='center')
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree_pagos.yview)
        vsb.pack(side='right', fill='y')
        self.tree_pagos.configure(yscrollcommand=vsb.set)
        self.tree_pagos.pack(fill='both', expand=True)
    def cargar_pagos(self):
        for item in self.tree_pagos.get_children():
            self.tree_pagos.delete(item)
        pagos = PagosBoleta.obtener_pagos_por_estudiante(self.carne)
        for p in pagos:
            self.tree_pagos.insert('', tk.END, values=(
                p['tipo_pago'],
                f"{p['monto_aplicado']:.2f}",
                p['descripcion'],
                p['no_boleta'],
                p['fecha_acreditacion'][:10]
            ))
class VentanaVerSaldos(tk.Toplevel):
    def __init__(self, master, carne_estudiante):
        super().__init__(master)
        self.carne = carne_estudiante
        self.title(f"Saldos a Favor - {self.carne}")
        self.geometry("400x200")
        self.transient(master)
        self.grab_set()
        tk.Label(self, text="Saldos a Favor Acumulados", font=('Arial', 14, 'bold')).pack(pady=10)
        frame = ttk.Frame(self, padding="15")
        frame.pack(padx=10, pady=10, fill='x')
        self.cargar_saldos(frame)
        ttk.Button(self, text="Cerrar", command=self.destroy).pack(pady=10)
    def cargar_saldos(self, frame):
        info = Estudiante.obtener_info(self.carne)
        if info:
            saldo_mensualidad = info['saldo_favor_mensualidad']
            saldo_otros = info['saldo_favor_otros']
            ttk.Label(frame, text="Saldo para Mensualidades:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ttk.Label(frame, text=f"Q.{saldo_mensualidad:,.2f}", font=('Arial', 12, 'bold'), foreground='blue').grid(
            row=0, column=1, padx=5, pady=5, sticky="e")
            ttk.Label(frame, text="Saldo para Otros Pagos:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            ttk.Label(frame, text=f"Q.{saldo_otros:,.2f}", font=('Arial', 12, 'bold'), foreground='green').grid(row=1,
            column=1, padx=5, pady=5, sticky="e")
            frame.grid_columnconfigure(1, weight=1)
        else:
            ttk.Label(frame, text="Error: Estudiante no encontrado.", foreground='red').pack()
class VentanaInscribirEstudiante(tk.Toplevel):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.title("Inscripción de Nuevo Estudiante")
        self.geometry("600x650")
        self.transient(master)
        self.grab_set()
        tk.Label(self, text="Registro de Nuevo Estudiante", font=('Arial', 16, 'bold')).pack(pady=15)
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill='both', expand=True)
        self.carreras = Carrera.obtener_todo()
        self.departamentos = Departamento.obtener_todo()
        campos = [
            ("Carné:", "entry_carne"),
            ("Nombre:", "entry_nombre"),
            ("Apellido:", "entry_apellido"),
            ("DPI:", "entry_dpi"),
            ("Edad:", "entry_edad"),
            ("Contraseña Inicial:", "entry_contrasena")
        ]
        self.entries = {}
        for i, (label_text, var_name) in enumerate(campos):
            ttk.Label(frame, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.entries[var_name] = entry
        self.entries['entry_contrasena'].config(show='*')
        row_carrera = len(campos)
        ttk.Label(frame, text="Carrera:").grid(row=row_carrera, column=0, padx=5, pady=5, sticky="w")
        self.var_carrera = tk.StringVar()
        opciones_carrera = [f"{c['id_carrera']}. {c['nombre']}" for c in self.carreras]
        self.combo_carrera = ttk.Combobox(frame, textvariable=self.var_carrera, values=opciones_carrera, state="readonly", width=38)
        self.combo_carrera.grid(row=row_carrera, column=1, padx=5, pady=5, sticky="ew")
        row_depa = row_carrera + 1
        ttk.Label(frame, text="Departamento:").grid(row=row_depa, column=0, padx=5, pady=5, sticky="w")
        self.var_depa = tk.StringVar()
        opciones_depa = [f"{d['id_depa']}. {d['nombre']}" for d in self.departamentos]
        self.combo_depa = ttk.Combobox(frame, textvariable=self.var_depa, values=opciones_depa, state="readonly", width=38)
        self.combo_depa.grid(row=row_depa, column=1, padx=5, pady=5, sticky="ew")
        self.combo_depa.bind('<<ComboboxSelected>>', self.actualizar_municipios)
        row_muni = row_depa + 1
        ttk.Label(frame, text="Municipio:").grid(row=row_muni, column=0, padx=5, pady=5, sticky="w")
        self.var_muni = tk.StringVar()
        self.combo_muni = ttk.Combobox(frame, textvariable=self.var_muni, state="readonly", width=38)
        self.combo_muni.grid(row=row_muni, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(self, text="Registrar Estudiante", command=self.guardar_estudiante).pack(pady=20)
    def actualizar_municipios(self, event=None):
        seleccion_depa = self.var_depa.get()
        if not seleccion_depa: return
        try:
            id_depa = int(seleccion_depa.split('.')[0])
            municipios = Municipio.obtener_por_depa(id_depa)
            opciones_muni = [f"{m['id_muni']}. {m['nombre']}" for m in municipios]
            self.combo_muni['values'] = opciones_muni
            self.var_muni.set('')
            if opciones_muni:
                self.combo_muni.set(opciones_muni[0])
            else:
                self.combo_muni.set("No hay municipios")
        except ValueError:
            pass
    def obtener_id_seleccionado(self, seleccion):
        try:
            return int(seleccion.split('.')[0])
        except:
            return None
    def guardar_estudiante(self):
        carne = self.entries['entry_carne'].get().strip()
        nombre = self.entries['entry_nombre'].get().strip()
        apellido = self.entries['entry_apellido'].get().strip()
        dpi = self.entries['entry_dpi'].get().strip()
        edad_str = self.entries['entry_edad'].get().strip()
        contrasena = self.entries['entry_contrasena'].get().strip()
        id_carrera = self.obtener_id_seleccionado(self.var_carrera.get())
        id_depa = self.obtener_id_seleccionado(self.var_depa.get())
        id_muni = self.obtener_id_seleccionado(self.var_muni.get())
        if not all([carne, nombre, apellido, dpi, edad_str, contrasena, id_carrera, id_depa, id_muni]):
            messagebox.showerror("Error de Validación", "Todos los campos son obligatorios.")
            return
        try:
            edad = int(edad_str)
            if edad <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error de Validación", "La edad debe ser un número entero positivo.")
            return
        estudiante = Estudiante(carne, nombre, apellido, dpi, edad, id_carrera, id_depa, id_muni)
        if estudiante.guardar(contrasena):
            messagebox.showinfo("Éxito", f"Estudiante {nombre} {apellido} (Carné: {carne}) inscrito correctamente.")
            self.destroy()
        else:
            messagebox.showerror("Error de Inscripción", "Error al guardar los datos. Verifique si el Carné o DPI ya están registrados.")
class VentanaAcreditarBoletas(tk.Toplevel):
    def __init__(self, master, app_instance, secretaria_id):
        super().__init__(master)
        self.app = app_instance
        self.secretaria_id = secretaria_id
        self.title("Acreditación de Boletas Pendientes")
        self.geometry("800x500")
        self.transient(master)
        self.grab_set()
        tk.Label(self, text="Boletas Pendientes de Acreditación", font=('Arial', 14, 'bold')).pack(pady=10)
        frame_tabla = ttk.Frame(self, padding="10")
        frame_tabla.pack(pady=10, padx=10, fill='both', expand=True)
        self.tree = ttk.Treeview(frame_tabla, columns=("No_Boleta", "Carne", "Nombre", "Monto", "Fecha"), show='headings')
        self.tree.heading("No_Boleta", text="No. Boleta")
        self.tree.heading("Carne", text="Carné Est.")
        self.tree.heading("Nombre", text="Estudiante")
        self.tree.heading("Monto", text="Monto (Q)")
        self.tree.heading("Fecha", text="F. Realización")
        self.tree.column("No_Boleta", width=100, anchor='center')
        self.tree.column("Carne", width=80, anchor='center')
        self.tree.column("Nombre", width=200)
        self.tree.column("Monto", width=80, anchor='e')
        self.tree.column("Fecha", width=100, anchor='center')
        vsb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_boleta)
        self.btn_acreditar = ttk.Button(self, text="Acreditar Boleta Seleccionada", command=self.iniciar_acreditacion, state=tk.DISABLED)
        self.btn_acreditar.pack(pady=10)
        self.cargar_boletas()
    def cargar_boletas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.boletas_pendientes = Boleta.listar_pendientes()
        if not self.boletas_pendientes:
            self.btn_acreditar.config(state=tk.DISABLED)
            return
        for boleta in self.boletas_pendientes:
            nombre_completo = f"{boleta['nombre']} {boleta['apellido']}"
            monto_formateado = f"{boleta['monto_depositado']:.2f}"
            self.tree.insert('', tk.END, values=(
                boleta['no_boleta'],
                boleta['carne'],
                nombre_completo,
                monto_formateado,
                boleta['fecha_realizacion']
            ), tags=(boleta['no_boleta'],))
    def seleccionar_boleta(self, event):
        items_seleccionados = self.tree.selection()
        if items_seleccionados:
            self.btn_acreditar.config(state=tk.NORMAL)
            self.boleta_seleccionada = self.tree.item(items_seleccionados[0], 'values')
        else:
            self.btn_acreditar.config(state=tk.DISABLED)
            self.boleta_seleccionada = None
    def iniciar_acreditacion(self):
        if not self.boleta_seleccionada:
            messagebox.showerror("Error", "Debe seleccionar una boleta.")
            return
        no_boleta = self.boleta_seleccionada[0]
        monto = float(self.boleta_seleccionada[3])
        VentanaAplicarPagos(self.master, self, no_boleta, monto, self.secretaria_id)
class VentanaAplicarPagos(tk.Toplevel):
    def __init__(self, master, parent_acreditacion, no_boleta, monto_total, secretaria_id):
        super().__init__(master)
        self.parent_acreditacion = parent_acreditacion
        self.no_boleta = no_boleta
        self.monto_restante = monto_total
        self.secretaria_id = secretaria_id
        self.title(f"Aplicar Pagos - Boleta {no_boleta} (Q.{monto_total:.2f})")
        self.geometry("700x550")
        self.transient(master)
        self.grab_set()
        self.pagos_aplicados = []
        self.boleta_info = Boleta.obtener_info_boleta(self.no_boleta)
        self.carne_estudiante = self.boleta_info['carne_estudiante']
        self.estudiante_info = Estudiante.obtener_info(self.carne_estudiante)
        self.costo_mensualidad = Carrera.obtener_costo_mensualidad(self.estudiante_info['id_carrera'])
        self.tipos_pagos = TipoPago.obtener_todo()
        tk.Label(self,
        text=f"Aplicar a Boleta {self.no_boleta} | Est.: {self.estudiante_info['nombre']} {self.estudiante_info['apellido']}",font=('Arial', 12)).pack(pady=5)
        frame_saldos = ttk.Frame(self, padding="10")
        frame_saldos.pack(pady=5, padx=10, fill='x')
        self.label_monto_restante = tk.Label(frame_saldos,
        text=f"MONTO RESTANTE DE BOLETA: Q.{self.monto_restante:.2f}", fg="red",font=('Arial', 12, 'bold'))
        self.label_monto_restante.pack(side='left', padx=10)
        self.label_saldo_mensualidad = tk.Label(frame_saldos, text="")
        self.label_saldo_mensualidad.pack(side='right')
        self.label_saldo_otros = tk.Label(frame_saldos, text="")
        self.label_saldo_otros.pack(side='right', padx=10)
        self.actualizar_saldos_ui()
        frame_seleccion = ttk.LabelFrame(self, text="1. Seleccionar Tipo de Pago", padding="10")
        frame_seleccion.pack(padx=10, fill='x')
        ttk.Label(frame_seleccion, text="Tipo de Pago:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.var_tipo_pago = tk.StringVar()
        opciones_pago = []
        for tp in self.tipos_pagos:
            costo = f"Q.{self.costo_mensualidad:.2f}" if tp['es_mensualidad'] else f"Q.{tp['monto_fijo']:.2f}"
            opciones_pago.append(f"{tp['id_tipo_pago']}. {tp['nombre']} (Costo: {costo})")
        self.combo_tipo_pago = ttk.Combobox(frame_seleccion, textvariable=self.var_tipo_pago, values=opciones_pago, state="readonly", width=50)
        self.combo_tipo_pago.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(frame_seleccion, text="Monto a Aplicar de BOLETA (Q):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_monto_aplicar = ttk.Entry(frame_seleccion, width=20)
        self.entry_monto_aplicar.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(frame_seleccion, text="Descripción:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_descripcion = ttk.Entry(frame_seleccion, width=50)
        self.entry_descripcion.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(frame_seleccion, text="Agregar Pago", command=self.agregar_pago).grid(row=3, column=1, pady=10, sticky='e')
        frame_aplicados = ttk.LabelFrame(self, text="2. Pagos Aplicados de esta Boleta", padding="10")
        frame_aplicados.pack(padx=10, pady=10, fill='both', expand=True)
        self.tree_pagos = ttk.Treeview(frame_aplicados, columns=("Tipo", "Aplicado", "Descripcion"), show='headings')
        self.tree_pagos.heading("Tipo", text="Tipo de Pago")
        self.tree_pagos.heading("Aplicado", text="Monto Aplicado (Q)")
        self.tree_pagos.heading("Descripcion", text="Descripción")
        self.tree_pagos.column("Tipo", width=150)
        self.tree_pagos.column("Aplicado", width=100, anchor='e')
        self.tree_pagos.column("Descripcion", width=350)
        self.tree_pagos.pack(fill='both', expand=True)
        frame_botones_final = ttk.Frame(self, padding="10")
        frame_botones_final.pack(fill='x', padx=10)
        ttk.Button(frame_botones_final, text="Cancelar / Descartar", command=self.destroy).pack(side='left', padx=10)
        ttk.Button(frame_botones_final, text="Finalizar y Acreditar Boleta", command=self.finalizar_acreditacion).pack(side='right', padx=10)
    def obtener_tipo_pago_por_nombre(self, seleccion):
        id_str = seleccion.split('.')[0]
        try:
            id_pago = int(id_str)
            return next((tp for tp in self.tipos_pagos if tp['id_tipo_pago'] == id_pago), None)
        except:
            return None
    def actualizar_saldos_ui(self):
        info = Estudiante.obtener_info(self.carne_estudiante)
        self.label_saldo_mensualidad.config(text=f"Saldo Mens.: Q.{info['saldo_favor_mensualidad']:.2f}")
        self.label_saldo_otros.config(text=f"Saldo Otros: Q.{info['saldo_favor_otros']:.2f}")
        self.label_monto_restante.config(text=f"MONTO RESTANTE DE BOLETA: Q.{self.monto_restante:.2f}")
    def agregar_pago(self):
        seleccion = self.var_tipo_pago.get()
        tipo_pago = self.obtener_tipo_pago_por_nombre(seleccion)
        descripcion = self.entry_descripcion.get().strip()
        if not tipo_pago or not descripcion:
            messagebox.showerror("Error", "Debe seleccionar un tipo de pago y añadir una descripción.")
            return
        try:
            monto_aplicar_boleta = float(self.entry_monto_aplicar.get())
        except ValueError:
            messagebox.showerror("Error", "Monto a aplicar de boleta debe ser un número válido.")
            return
        if monto_aplicar_boleta < 0:
            messagebox.showerror("Error", "El monto a aplicar no puede ser negativo.")
            return
        monto_aplicar_boleta_real = min(monto_aplicar_boleta, self.monto_restante)
        info_actual = Estudiante.obtener_info(self.carne_estudiante)
        es_mensualidad = tipo_pago['es_mensualidad']
        costo_esperado = self.costo_mensualidad if es_mensualidad else tipo_pago['monto_fijo']
        saldo_a_usar_disponible = info_actual['saldo_favor_mensualidad'] if es_mensualidad else info_actual[
            'saldo_favor_otros']
        monto_a_cubrir_inicial = costo_esperado
        monto_aplicado_total = 0.0
        if saldo_a_usar_disponible > 0.01:
            respuesta = messagebox.askyesno("Usar Saldo a Favor",f"¿Desea usar Q.{saldo_a_usar_disponible:.2f} de saldo a favor para este pago (Costo Q.{costo_esperado:.2f})?")
            if respuesta:
                monto_usado_saldo = min(saldo_a_usar_disponible, monto_a_cubrir_inicial)
                Estudiante.usar_saldo(self.carne_estudiante, es_mensualidad, monto_usado_saldo)
                self.pagos_aplicados.append({
                    'no_boleta': self.no_boleta,
                    'id_tipo_pago': tipo_pago['id_tipo_pago'],
                    'monto_aplicado': monto_usado_saldo,
                    'descripcion': f"Uso de saldo a favor. Cubre Q.{monto_usado_saldo:.2f} de {tipo_pago['nombre']}.",
                    'tipo_nombre': tipo_pago['nombre'] + " (SALDO)"
                })
                monto_a_cubrir_inicial -= monto_usado_saldo
                monto_aplicado_total += monto_usado_saldo
        if monto_aplicar_boleta_real > 0.01:
            self.pagos_aplicados.append({
                'no_boleta': self.no_boleta,
                'id_tipo_pago': tipo_pago['id_tipo_pago'],
                'monto_aplicado': monto_aplicar_boleta_real,
                'descripcion': descripcion,
                'tipo_nombre': tipo_pago['nombre']
            })
            monto_aplicado_total += monto_aplicar_boleta_real
            self.monto_restante -= monto_aplicar_boleta_real
            if monto_aplicado_total > costo_esperado:
                saldo_generado = monto_aplicado_total - costo_esperado
                Estudiante.actualizar_saldo(self.carne_estudiante, es_mensualidad, saldo_generado)
                messagebox.showinfo("Saldo Generado",f"Pago cubierto. Se generó Q.{saldo_generado:.2f} de saldo a favor en {'mensualidad' if es_mensualidad else 'otros'}.")
        self.actualizar_treeview_pagos()
        self.actualizar_saldos_ui()
        self.entry_monto_aplicar.delete(0, tk.END)
        self.entry_descripcion.delete(0, tk.END)
        self.var_tipo_pago.set('')
    def actualizar_treeview_pagos(self):
        for item in self.tree_pagos.get_children():
            self.tree_pagos.delete(item)
        for pago in self.pagos_aplicados:
            self.tree_pagos.insert('', tk.END, values=(
                pago['tipo_nombre'],
                f"{pago['monto_aplicado']:.2f}",
                pago['descripcion']
            ))
    def finalizar_acreditacion(self):
        if not self.pagos_aplicados:
            messagebox.showerror("Error", "Debe aplicar al menos un pago.")
            return
        if self.monto_restante > 0.01:
            respuesta = messagebox.askyesno("Monto Restante", f"Quedan Q.{self.monto_restante:.2f} restantes de la boleta. ¿Desea agregarlo a 'Saldo a Favor - Otros' del estudiante?")
            if respuesta:
                Estudiante.actualizar_saldo(self.carne_estudiante, False, self.monto_restante)
                self.monto_restante = 0.0
            else:
                messagebox.showwarning("Proceso Cancelado", "El monto restante no fue aplicado. La boleta queda PENDIENTE de acreditar.")
                return
        for p in self.pagos_aplicados:
            if not p['tipo_nombre'].endswith("(SALDO)"):
                PagosBoleta.guardar_pago(p['no_boleta'], p['id_tipo_pago'], p['monto_aplicado'], p['descripcion'])
        if not Boleta.acreditar(self.no_boleta, self.secretaria_id):
            messagebox.showerror("Error de Base de Datos", "Ocurrió un error al marcar la boleta como acreditada. Contacte al administrador.")
            return
        messagebox.showinfo("Éxito", f"Boleta {self.no_boleta} ACREDITADA y pagos aplicados exitosamente.")
        self.parent_acreditacion.cargar_boletas()  # <--- Ahora esto se ejecuta
        self.destroy()
class VentanaConsultaPagosSecretaria(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Consulta de Pagos por Carné")
        self.geometry("850x500")
        self.transient(master)
        self.grab_set()
        tk.Label(self, text="Registro de Pagos Aplicados por Estudiante", font=('Arial', 14, 'bold')).pack(pady=10)
        frame_busqueda = ttk.Frame(self, padding="10")
        frame_busqueda.pack(pady=5, padx=10, fill='x')
        ttk.Label(frame_busqueda, text="Ingresar Carné:").pack(side='left', padx=5)
        self.entry_carne = ttk.Entry(frame_busqueda, width=15)
        self.entry_carne.pack(side='left', padx=5)
        ttk.Button(frame_busqueda, text="Buscar Pagos", command=self.cargar_pagos).pack(side='left', padx=10)
        self.label_nombre_estudiante = ttk.Label(frame_busqueda, text="")
        self.label_nombre_estudiante.pack(side='left', padx=20)
        frame_resultados = ttk.Frame(self, padding="10")
        frame_resultados.pack(pady=10, padx=10, expand=True, fill='both')
        self.crear_tabla_pagos(frame_resultados)
    def crear_tabla_pagos(self, frame):
        self.tree_pagos = ttk.Treeview(frame, columns=("Tipo", "Monto", "Descripcion", "Boleta", "F_Acredit"), show='headings')
        self.tree_pagos.heading("Tipo", text="Tipo de Pago")
        self.tree_pagos.heading("Monto", text="Monto Aplicado (Q)")
        self.tree_pagos.heading("Descripcion", text="Descripción")
        self.tree_pagos.heading("Boleta", text="No. Boleta")
        self.tree_pagos.heading("F_Acredit", text="F. Acreditación")
        self.tree_pagos.column("Tipo", width=150)
        self.tree_pagos.column("Monto", width=120, anchor='e')
        self.tree_pagos.column("Descripcion", width=300)
        self.tree_pagos.column("Boleta", width=100, anchor='center')
        self.tree_pagos.column("F_Acredit", width=120, anchor='center')
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree_pagos.yview)
        vsb.pack(side='right', fill='y')
        self.tree_pagos.configure(yscrollcommand=vsb.set)
        self.tree_pagos.pack(fill='both', expand=True)
    def cargar_pagos(self):
        carne = self.entry_carne.get().strip()
        for item in self.tree_pagos.get_children():
            self.tree_pagos.delete(item)
        self.label_nombre_estudiante.config(text="")
        if not carne:
            messagebox.showerror("Error", "Debe ingresar un número de Carné.")
            return
        estudiante_info = Estudiante.obtener_info(carne)
        if not estudiante_info:
            messagebox.showerror("Error", f"No se encontró un estudiante con el Carné: {carne}")
            return
        nombre_completo = f"{estudiante_info['nombre']} {estudiante_info['apellido']}"
        self.label_nombre_estudiante.config(text=f"Estudiante: {nombre_completo}")
        pagos = PagosBoleta.obtener_pagos_por_estudiante(carne)
        if not pagos:
            messagebox.showinfo("Sin Pagos", f"El estudiante {nombre_completo} no tiene pagos registrados.")
            return
        for p in pagos:
            self.tree_pagos.insert('', tk.END, values=(
                p['tipo_pago'],
                f"{p['monto_aplicado']:.2f}",
                p['descripcion'],
                p['no_boleta'],
                p['fecha_acreditacion'][:10]
            ))
class AplicacionGestionAcademica:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de Gestión Académica")

        try:
            configurar_base_datos()
        except Exception as e:
            messagebox.showerror("Error de DB", f"No se pudo configurar la base de datos: {e}")
            self.master.destroy()
            return
        self.login_window = VentanaLogin(master, self)
    def mostrar_menu_principal(self, tipo_usuario, usuario):
        if tipo_usuario == "ESTUDIANTE":
            self.ventana_menu = VentanaMenuEstudiante(self.master, self, usuario)
        elif tipo_usuario == "SECRETARIA":
            self.ventana_menu = VentanaMenuSecretaria(self.master, self, usuario)
        self.master.deiconify()
    def volver_a_login(self):
        if hasattr(self, 'ventana_menu'):
            self.ventana_menu.destroy()
        self.login_window = VentanaLogin(self.master, self)
if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionGestionAcademica(root)
    root.mainloop()
