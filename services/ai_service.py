from collections import Counter

from supabase_config import supabase


# ==========================================
# OBTENER DATOS
# ==========================================

def obtener_solicitudes():

    return (
        supabase
        .table("solicitudes")
        .select("*")
        .execute()
        .data
    )


def obtener_historial():

    return (
        supabase
        .table("historial")
        .select("*")
        .execute()
        .data
    )


def obtener_accesos():

    return (
        supabase
        .table("accesos")
        .select("*")
        .execute()
        .data
    )


# ==========================================
# RESUMEN GENERAL
# ==========================================

def obtener_resumen_general():

    try:

        solicitudes = obtener_solicitudes()
        historial = obtener_historial()
        accesos = obtener_accesos()

        abiertas = [
            s
            for s in solicitudes
            if s.get("estatus")
            not in [
                "PRODUCTIVA",
                "IMPRODUCTIVA",
                "CERRADA"
            ]
        ]

        return f"""
📊 RESUMEN TRADE

Solicitudes Totales:
{len(solicitudes)}

Solicitudes Abiertas:
{len(abiertas)}

Movimientos Historial:
{len(historial)}

Accesos Registrados:
{len(accesos)}
"""

    except Exception as e:

        return f"Error: {e}"


# ==========================================
# BUSQUEDA DE FOLIOS
# ==========================================

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

            return (
                f"No encontré el folio {folio}"
            )

        datos = solicitud[0]

        historial = (
            supabase
            .table("historial")
            .select("*")
            .eq("folio", folio)
            .execute()
            .data
        )

        return f"""
📋 FOLIO

Folio:
{folio}

Estatus:
{datos.get("estatus")}

Negocio:
{datos.get("negocio")}

Canal:
{datos.get("canal")}

GEC:
{datos.get("gec")}

Usuario:
{datos.get("usuario")}

Movimientos:
{len(historial)}
"""

    except Exception as e:

        return f"Error: {e}"


# ==========================================
# ABIERTAS
# ==========================================

def solicitudes_abiertas():

    solicitudes = obtener_solicitudes()

    abiertas = [
        s
        for s in solicitudes
        if s.get("estatus")
        not in [
            "PRODUCTIVA",
            "IMPRODUCTIVA",
            "CERRADA"
        ]
    ]

    return f"""
📂 SOLICITUDES ABIERTAS

Total:
{len(abiertas)}
"""


# ==========================================
# PRODUCTIVAS
# ==========================================

def solicitudes_productivas():

    solicitudes = obtener_solicitudes()

    total = len([
        s
        for s in solicitudes
        if s.get("estatus")
        == "PRODUCTIVA"
    ])

    return f"""
✅ PRODUCTIVAS

Total:
{total}
"""


# ==========================================
# IMPRODUCTIVAS
# ==========================================

def solicitudes_improductivas():

    solicitudes = obtener_solicitudes()

    total = len([
        s
        for s in solicitudes
        if s.get("estatus")
        == "IMPRODUCTIVA"
    ])

    return f"""
❌ IMPRODUCTIVAS

Total:
{total}
"""


# ==========================================
# TOP MODELOS
# ==========================================

def top_modelos():

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

    top = contador.most_common(10)

    respuesta = "🏆 TOP MODELOS\n\n"

    for modelo, cantidad in top:

        respuesta += (
            f"• {modelo}: {cantidad}\n"
        )

    return respuesta


# ==========================================
# TOP JEFATURAS
# ==========================================

def top_jefaturas():

    solicitudes = obtener_solicitudes()

    contador = Counter()

    for fila in solicitudes:

        valor = fila.get("jefatura")

        if valor:

            contador[valor] += 1

    top = contador.most_common(10)

    respuesta = "🏆 TOP JEFATURAS\n\n"

    for nombre, cantidad in top:

        respuesta += (
            f"• {nombre}: {cantidad}\n"
        )

    return respuesta


# ==========================================
# TOP CANALES
# ==========================================

def top_canales():

    solicitudes = obtener_solicitudes()

    contador = Counter()

    for fila in solicitudes:

        valor = fila.get("canal")

        if valor:

            contador[valor] += 1

    top = contador.most_common(10)

    respuesta = "🏆 TOP CANALES\n\n"

    for nombre, cantidad in top:

        respuesta += (
            f"• {nombre}: {cantidad}\n"
        )

    return respuesta


# ==========================================
# TOP GEC
# ==========================================

def top_gec():

    solicitudes = obtener_solicitudes()

    contador = Counter()

    for fila in solicitudes:

        valor = fila.get("gec")

        if valor:

            contador[valor] += 1

    top = contador.most_common(10)

    respuesta = "🏆 TOP GEC\n\n"

    for nombre, cantidad in top:

        respuesta += (
            f"• {nombre}: {cantidad}\n"
        )

    return respuesta


# ==========================================
# RESPONDER IA
# ==========================================

def responder_trade_ai(pregunta):

    pregunta = pregunta.upper().strip()

    if pregunta == "RESUMEN":

        return obtener_resumen_general()

    if pregunta == "ABIERTAS":

        return solicitudes_abiertas()

    if pregunta == "PRODUCTIVAS":

        return solicitudes_productivas()

    if pregunta == "IMPRODUCTIVAS":

        return solicitudes_improductivas()

    if pregunta == "TOP MODELOS":

        return top_modelos()

    if pregunta == "TOP JEFATURAS":

        return top_jefaturas()

    if pregunta == "TOP CANALES":

        return top_canales()

    if pregunta == "TOP GEC":

        return top_gec()

    if "FOLIO" in pregunta:

        partes = pregunta.split()

        for palabra in partes:

            if palabra.startswith("TRD"):

                return buscar_folio(
                    palabra
                )

    return """
🤖 TRADE AI

Comandos disponibles:

• RESUMEN
• ABIERTAS
• PRODUCTIVAS
• IMPRODUCTIVAS
• TOP MODELOS
• TOP JEFATURAS
• TOP CANALES
• TOP GEC
• FOLIO TRD-XXXXXX
"""
