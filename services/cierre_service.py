from datetime import datetime, timedelta
from supabase_config import supabase


def cerrar_solicitudes_vencidas() -> int:
    """Busca solicitudes con estatus 'CAPTURADA' con 30 o más días de antigüedad 
    y las actualiza a 'CANCELADA' en Supabase.
    """
    try:
        hace_30_dias = (datetime.now() - timedelta(days=30)).isoformat()

        res = (
            supabase.table("solicitudes")
            .select("folio")
            .eq("estatus", "CAPTURADA")
            .lt("fecha", hace_30_dias)
            .execute()
        )

        solicitudes_vencidas = res.data
        if not solicitudes_vencidas:
            return 0

        folios = [s["folio"] for s in solicitudes_vencidas]

        supabase.table("solicitudes").update({
            "estatus": "CANCELADA",
            "comentarios_admin": "Cierre automático por antigüedad"
        }).in_("folio", folios).execute()

        return len(folios)

    except Exception as e:
        print(f"Error cerrando solicitudes en Supabase: {e}")
        return 0
