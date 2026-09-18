from supabase_config import supabase


def guardar_historial(
    folio: str,
    usuario: str,
    accion: str
) -> None:
    """Registra una acción en el historial asociada a un folio."""

    supabase.table(
        "historial"
    ).insert(
        {
            "folio": folio,
            "usuario": usuario,
            "accion": accion
        }
    ).execute()
