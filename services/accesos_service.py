from supabase_config import supabase


def registrar_acceso(
    usuario: str,
    accion: str,
    ip: str = ""
) -> None:
    """Registra una acción de acceso de usuario en la tabla de auditoría."""

    supabase.table(
        "accesos"
    ).insert(
        {
            "usuario": usuario,
            "accion": accion,
            "ip": ip
        }
    ).execute()
