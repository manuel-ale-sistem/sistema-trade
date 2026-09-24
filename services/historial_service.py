from supabase_config import supabase


def guardar_historial(
    folio: str,
    usuario: str,
    accion: str
) -> None:

    try:

        supabase.table(
            "historial"
        ).insert(
            {
                "folio": folio,
                "usuario": usuario,
                "accion": accion
            }
        ).execute()

    except Exception as e:

        print(
            f"Error guardando historial: {e}"
        )
