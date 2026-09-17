from database import get_connection


def guardar_historial(folio: str, usuario: str, accion: str) -> None:
    """Registra una acción en el historial de auditoría asociada a un folio y un usuario."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        cur.execute(
            """
            INSERT INTO historial(
                folio,
                usuario,
                accion
            )
            VALUES(?, ?, ?)
            """,
            (
                folio,
                usuario,
                accion
            )
        )
        
        conn.commit()
    finally:
        conn.close()