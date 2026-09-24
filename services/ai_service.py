from supabase_config import supabase
import pandas as pd
from collections import Counter


def obtener_solicitudes():
    return (
        supabase
        .table("solicitudes")
        .select("*")
        .execute()
        .data
    )


def top_jefaturas():
    solicitudes = obtener_solicitudes()
    contador = Counter()

    for fila in solicitudes:
        jefatura = fila.get("jefatura")
        if jefatura:
            contador[jefatura] += 1

    top = contador.most_common(5)
    respuesta = "🏆 TOP JEFATURAS\n\n"

    for nombre, cantidad in top:
        respuesta += f"- {nombre}: {cantidad} solicitudes\n"

    return respuesta


def top_modelos():
    try:
        detalles = (
            supabase
            .table("solicitud_detalle")
            .select("modelo")
            .execute()
            .data
        )

        contador = Counter()
        for fila in detalles:
            modelo = fila.get("modelo")
            if modelo:
                contador[modelo] += 1

        top = contador.most_common(5)
        respuesta = "🏆 TOP MODELOS\n\n"

        for modelo, cantidad in top:
            respuesta += f"- {modelo}: {cantidad}\n"

        return respuesta
    except Exception as e:
        return f"Error al consultar modelos: {e}"


def solicitudes_improductivas():
    solicitudes = obtener_solicitudes()
    total = len(
        [
            s
            for s in solicitudes
            if s.get("estatus") == "IMPRODUCTIVA"
        ]
    )

    return f"""❌ SOLICITUDES IMPRODUCTIVAS

Total: {total}
"""


def solicitudes_productivas():
    solicitudes = obtener_solicitudes()
    total = len(
        [
            s
            for s in solicitudes
            if s.get("estatus") == "PRODUCTIVA"
        ]
    )

    return f"""✅ SOLICITUDES PRODUCTIVAS

Total: {total}
"""


def solicitudes_abiertas():
    solicitudes = obtener_solicitudes()
    abiertas = [
        s
        for s in solicitudes
        if s.get("estatus") not in [
            "PRODUCTIVA",
            "IMPRODUCTIVA",
            "CERRADA"
        ]
    ]

    return f"""📂 SOLICITUDES ABIERTAS

Total: {len(abiertas)}"""


def obtener_resumen_general():
    try:
        solicitudes = obtener_solicitudes()
        
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
                if s.get("estatus") not in ["PRODUCTIVA", "IMPRODUCTIVA", "CERRADA"]
            ]
        )

        return f"""📊 RESUMEN TRADE

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

        respuesta = f"""📋 FOLIO: {folio}

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

    if "ABIERTAS" in pregunta:
        return solicitudes_abiertas()

    if "PRODUCTIVAS" in pregunta and "IMPRODUCTIVAS" not in pregunta:
        return solicitudes_productivas()

    if "IMPRODUCTIVAS" in pregunta:
        return solicitudes_improductivas()

    if "JEFATURAS" in pregunta or "TOP JEFATURAS" in pregunta:
        return top_jefaturas()

    if "MODELOS" in pregunta or "TOP MODELOS" in pregunta:
        return top_modelos()

    if "FOLIO" in pregunta:
        partes = pregunta.split()
        for palabra in partes:
            if palabra.startswith("TRD"):
                return buscar_folio(palabra)

    return """🤖 Trade AI - ¿Qué deseas consultar?

Puedes preguntar:
- RESUMEN
- ABIERTAS
- PRODUCTIVAS
- IMPRODUCTIVAS
- TOP JEFATURAS
- TOP MODELOS
- FOLIO TRD-XXXXX
"""
