from supabase_config import supabase
import pandas as pd


def obtener_resumen_general():

    try:

        solicitudes = (
            supabase
            .table("solicitudes")
            .select("*")
            .execute()
            .data
        )

        historial = (
            supabase
            .table("historial")
            .select("*")
            .execute()
            .data
        )

        accesos = (
            supabase
            .table("accesos")
            .select("*")
            .execute()
            .data
        )

        total_solicitudes = len(solicitudes)
        total_historial = len(historial)
        total_accesos = len(accesos)

        abiertas = len(
            [
                s
                for s in solicitudes
                if s.get("estatus")
                not in ["PRODUCTIVA", "IMPRODUCTIVA", "CERRADA"]
            ]
        )

        return f"""
📊 RESUMEN TRADE

Solicitudes Totales: {total_solicitudes}

Solicitudes Abiertas: {abiertas}

Movimientos Historial: {total_historial}

Accesos Registrados: {total_accesos}
"""

    except Exception as e:

        return f"Error: {e}"


def buscar_folio(folio):

    try:

        solicitud = (
            supabase
            .table("solicitudes")
            .select("*")
            .eq("folio", folio)
            .execute()
            .data
        )

        if not solicitud:

            return f"No encontré el folio {folio}"

        datos = solicitud[0]

        movimientos = (
            supabase
            .table("historial")
            .select("*")
            .eq("folio", folio)
            .execute()
            .data
        )

        respuesta = f"""
📋 FOLIO: {folio}

Estatus: {datos.get("estatus")}

Negocio: {datos.get("negocio")}

Canal: {datos.get("canal")}

GEC: {datos.get("gec")}

Usuario: {datos.get("usuario")}

Movimientos registrados: {len(movimientos)}
"""

        return respuesta

    except Exception as e:

        return f"Error: {e}"


def responder_trade_ai(pregunta):

    pregunta = pregunta.upper().strip()

    if "RESUMEN" in pregunta:

        return obtener_resumen_general()

    if "FOLIO" in pregunta:

        partes = pregunta.split()

        for palabra in partes:

            if palabra.startswith("TRD"):

                return buscar_folio(
                    palabra
                )

    return """
🤖 Trade AI

Puedes preguntar:

- RESUMEN
- FOLIO TRD-XXXXX
"""
