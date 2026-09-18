from supabase_config import supabase


def registrar_acceso(
    usuario: str,
    accion: str,
    ip: str = ""
) -> None:
    try:
        supabase.table(
            "accesos"
        ).insert(
            {
                "usuario": usuario,
                "accion": accion,
                "ip": ip
            }
        ).execute()

    except Exception as e:
        print(
            f"Error registrando acceso: {e}"
        )
