from database import get_connection


def cerrar_solicitudes_vencidas() -> int:
    """Busca solicitudes con estatus 'CAPTURADA' que tengan 30 o más días de antigüedad
    desde su fecha de creación y las cambia automáticamente a estatus 'CANCELADA'.

    Returns:
        int: Número de solicitudes que fueron cerradas/canceladas automáticamente.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE solicitudes
            SET
                estatus = 'CANCELADA',
                comentarios_admin = 'Cierre automático por antigüedad'
            WHERE estatus = 'CAPTURADA'
            AND (
                julianday('now')
                -
                julianday(fecha)
            ) >= 30
            """
        )

        registros = cur.rowcount
        conn.commit()
        return registros
        
    finally:
        conn.close()