import sqlite3
import bcrypt

DB_NAME = "trade.db"


# ==========================================
# CONEXION
# ==========================================

def get_connection():
    """Crea y devuelve una conexión a SQLite con soporte para diccionarios en filas y timeout."""
    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False,
        timeout=30
    )
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# PASSWORD
# ==========================================

def hash_password(password):
    """Genera un hash seguro para la contraseña usando bcrypt."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


# ==========================================
# CREAR TABLAS
# ==========================================

def create_tables():
    """Crea todas las tablas e índices necesarios si no existen."""
    conn = get_connection()
    cur = conn.cursor()

    # ==========================
    # USUARIOS
    # ==========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        password TEXT,
        nombre TEXT,
        rol TEXT,
        activo INTEGER DEFAULT 1
    )
    """)

    # ==========================
    # SOLICITUDES
    # ==========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS solicitudes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT UNIQUE,
        fecha TEXT,
        jefatura TEXT,
        ruta TEXT,
        asesor TEXT,
        canal TEXT,
        solicitud TEXT,
        ppa TEXT,
        sap TEXT,
        negocio TEXT,
        telefono TEXT,
        gec TEXT,
        modelo TEXT,
        segmento TEXT,
        latitud TEXT,
        longitud TEXT,
        url_maps TEXT,
        observaciones TEXT,
        estatus TEXT,
        resultado TEXT,
        comentarios_admin TEXT,
        usuario TEXT,
        usuario_gestiona TEXT,
        fecha_cierre TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ==========================
    # DETALLE DE SOLICITUDES
    # ==========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS solicitud_detalle(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT NOT NULL,
        categoria TEXT,
        tipo_solicitud TEXT,
        modelo TEXT,
        cantidad INTEGER DEFAULT 1,
        serie TEXT,
        comentarios TEXT,
        estatus TEXT DEFAULT 'CAPTURADO',
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ==========================
    # MODELOS DETALLE
    # ==========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS modelos_detalle(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        catalogo_id INTEGER UNIQUE,
        capacidad TEXT,
        voltaje TEXT,
        puertas TEXT,
        refrigerante TEXT,
        consumo TEXT,
        temperatura TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(catalogo_id)
        REFERENCES catalogos(id)
    )
    """)

    # ==========================
    # DOCUMENTOS
    # ==========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS documentos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT,
        archivo TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ==========================
    # HISTORIAL
    # ==========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS historial(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT,
        usuario TEXT,
        accion TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ==========================
    # ACCESOS
    # ==========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS accesos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        accion TEXT,
        ip TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ==========================
    # CATALOGOS
    # ==========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS catalogos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        valor TEXT,
        activo INTEGER DEFAULT 1
    )
    """)

    # ==========================
    # MIGRACION AUTOMATICA CATALOGOS
    # ==========================
    columnas = [
        row[1] for row in cur.execute("PRAGMA table_info(catalogos)")
    ]

    if "eliminado" not in columnas:
        cur.execute(
            """
            ALTER TABLE catalogos
            ADD COLUMN eliminado INTEGER DEFAULT 0
            """
        )

    if "imagen_path" not in columnas:
        cur.execute(
            """
            ALTER TABLE catalogos
            ADD COLUMN imagen_path TEXT
            """
        )
        
    if "pdf_path" not in columnas:
        cur.execute("""
        ALTER TABLE catalogos
        ADD COLUMN pdf_path TEXT
        """)        

    # ==========================
    # MIGRACION AUTOMATICA SOLICITUD_DETALLE
    # ==========================
    columnas_detalle = [
        row[1]
        for row in cur.execute(
            "PRAGMA table_info(solicitud_detalle)"
        )
    ]

    if "reporte" not in columnas_detalle:
        cur.execute("""
        ALTER TABLE solicitud_detalle
        ADD COLUMN reporte TEXT
        """)

    if "material" not in columnas_detalle:
        cur.execute("""
        ALTER TABLE solicitud_detalle
        ADD COLUMN material TEXT
        """)

    if "capacidad_actual" not in columnas_detalle:
        cur.execute("""
        ALTER TABLE solicitud_detalle
        ADD COLUMN capacidad_actual TEXT
        """)

    if "capacidad_solicitada" not in columnas_detalle:
        cur.execute("""
        ALTER TABLE solicitud_detalle
        ADD COLUMN capacidad_solicitada TEXT
        """)
        
    # ==========================
    # INDICES
    # ==========================
    cur.execute("CREATE INDEX IF NOT EXISTS idx_folio ON solicitudes(folio)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_estatus ON solicitudes(estatus)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sap ON solicitudes(sap)")

    conn.commit()
    conn.close()


# ==========================================
# CREAR ADMIN
# ==========================================

def crear_admin():
    """Crea un usuario administrador por defecto si no existe."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id
        FROM usuarios
        WHERE usuario = ?
        """,
        ("admin",)
    )

    existe = cur.fetchone()

    if not existe:
        cur.execute(
            """
            INSERT INTO usuarios(
                usuario,
                password,
                nombre,
                rol
            )
            VALUES(?, ?, ?, ?)
            """,
            (
                "admin",
                hash_password("admin123"),
                "ADMINISTRADOR",
                "ADMIN"
            )
        )

    conn.commit()
    conn.close()


# ==========================================
# CATALOGOS BASE
# ==========================================

def crear_catalogos_base():
    """Inserta catálogos por defecto si aún no están registrados."""
    conn = get_connection()
    cur = conn.cursor()

    catalogos = [
        ("CANAL", "Canal Moderno"),
        ("CANAL", "Centro de Consumo"),
        ("CANAL", "Punto de Venta"),
        ("CANAL", "Six"),
        ("GEC", "ORO"),
        ("GEC", "PLATA"),
        ("GEC", "PLATINO"),
        ("GEC", "TITANIUM")
    ]

    for tipo, valor in catalogos:
        cur.execute(
            """
            SELECT id
            FROM catalogos
            WHERE tipo = ?
            AND valor = ?
            """,
            (tipo, valor)
        )

        existe = cur.fetchone()

        if not existe:
            cur.execute(
                """
                INSERT INTO catalogos(
                    tipo,
                    valor
                )
                VALUES(?, ?)
                """,
                (tipo, valor)
            )

    conn.commit()
    conn.close()


# ==========================================
# FUNCIONES AUXILIARES PARA CATALOGOS CON IMAGEN
# ==========================================

def insertar_catalogo_con_imagen(tipo, valor, imagen_path=""):
    """Inserta un elemento en el catálogo con su respectiva ruta de imagen opcional."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO catalogos (tipo, valor, imagen_path, activo, eliminado)
            VALUES (?, ?, ?, 1, 0)
            """,
            (tipo, valor, imagen_path)
        )
        conn.commit()
        exito = True
    except Exception as e:
        print(f"Error al insertar catálogo: {e}")
        exito = False
    finally:
        conn.close()
    return exito


def obtener_catalogos_por_tipo(tipo):
    """Obtiene todos los registros activos de un tipo de catálogo específico."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, valor, imagen_path, pdf_path 
        FROM catalogos 
        WHERE tipo = ? AND activo = 1 AND (eliminado = 0 OR eliminado IS NULL)
        """,
        (tipo,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# ==========================================
# GUARDAR DETALLE DE SOLICITUD
# ==========================================

def guardar_detalle_solicitud(
    cur,
    folio,
    categoria,
    tipo_solicitud,
    modelo="",
    cantidad=1,
    serie="",
    comentarios="",
    reporte="",
    material="",
    capacidad_actual="",
    capacidad_solicitada=""
):

    cur.execute(
        """
        INSERT INTO solicitud_detalle(

            folio,
            categoria,
            tipo_solicitud,
            modelo,
            cantidad,
            serie,
            comentarios,
            reporte,
            material,
            capacidad_actual,
            capacidad_solicitada

        )
        VALUES(
            ?,?,?,?,?,?,?,
            ?,?,?,?
        )
        """,
        (
            folio,
            categoria,
            tipo_solicitud,
            modelo,
            cantidad,
            serie,
            comentarios,
            reporte,
            material,
            capacidad_actual,
            capacidad_solicitada
        )
    )


# ==========================================
# GUARDAR ESPECIFICACIONES DE MODELOS
# ==========================================

def guardar_especificaciones(catalogo_id, datos):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO modelos_detalle(
            catalogo_id,
            capacidad,
            voltaje,
            puertas,
            refrigerante,
            consumo,
            temperatura
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        catalogo_id,
        datos.get("capacidad"),
        datos.get("voltaje"),
        datos.get("puertas"),
        datos.get("refrigerante"),
        datos.get("consumo"),
        datos.get("temperatura")
    ))

    conn.commit()
    conn.close()