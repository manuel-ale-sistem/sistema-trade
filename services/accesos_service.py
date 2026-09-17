from database import get_connection


def registrar_acceso(usuario: str, accion: str, ip: str = "") -> None:
    """Registra una acción de acceso de usuario en la tabla de auditoría."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO accesos(
                usuario,
                accion,
                ip
            )
            VALUES(?, ?, ?)
            """,
            (
                usuario,
                accion,
                ip
            )
        )
        conn.commit()
    finally:
        conn.close()