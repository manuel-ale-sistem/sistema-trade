import bcrypt

from database import get_connection
from services.accesos_service import registrar_acceso


# ==========================================
# VERIFICAR PASSWORD
# ==========================================

def verificar_password(password, password_hash):
    """Verifica si la contraseña coincide con el hash almacenado."""
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


# ==========================================
# LOGIN
# ==========================================

def login(usuario, password):
    """Valida las credenciales del usuario y registra el acceso si son correctas."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM usuarios
        WHERE usuario = ?
        AND activo = 1
        """,
        (usuario,)
    )

    datos = cur.fetchone()
    conn.close()

    if not datos:
        return None

    try:
        # Nota: 'datos' debe permitir acceso por clave (ej. diccionario) 
        # asegurando que get_connection() tenga configured row_factory.
        if verificar_password(password, datos["password"]):
            registrar_acceso(usuario, "LOGIN")
            return datos
    except Exception:
        return None

    return None