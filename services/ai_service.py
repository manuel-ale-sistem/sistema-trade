from collections import Counter
import streamlit as st
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


def obtener_metricas():
    solicitudes = obtener_solicitudes()
    total = len(solicitudes)
    abiertas = len([
        s
        for s in solicitudes
        if s.get("estatus")
        not in [
            "PRODUCTIVA",
            "IMPRODUCTIVA",
            "CERRADA"
        ]
    ])
    productivas = len([
        s
        for s in solicitudes
        if s.get("estatus")
        == "PRODUCTIVA"
    ])
    improductivas = len([
        s
        for s in solicitudes
        if s.get("estatus")
        == "IMPRODUCTIVA"
    ])
    return {
        "total": total,
        "abiertas": abiertas,
        "productivas": productivas,
        "improductivas": improductivas
    }


def ultimos_folios():
    try:
        datos = (
            supabase
            .table("solicitudes")
            .select(
                "folio,negocio,estatus"
            )
            .order(
                "fecha",
                desc=True
            )
            .limit(5)
            .execute()
            .data
        )
        return datos
    except Exception:
        return []


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
            return f"No encontré el folio {folio}"

        datos = solicitud[0]

        # MEMORIA DEL ÚLTIMO FOLIO
        st.session_state[
            "ultimo_folio_ai"
        ] = folio

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
# CONSULTAR ÚLTIMO FOLIO EN MEMORIA
# ==========================================

def consultar_ultimo_folio():
    folio = st.session_state.get(
        "ultimo_folio_ai"
    )
    if not folio:
        return """
No tengo un folio en contexto.
Primero consulta algo como:
FOLIO TRD-000001
"""
    return buscar_folio(folio)


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
        respuesta += f"• {modelo}: {cantidad}\n"

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
        respuesta += f"• {nombre}: {cantidad}\n"

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
        respuesta += f"• {nombre}: {cantidad}\n"

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
        respuesta += f"• {nombre}: {cantidad}\n"

    return respuesta


# ==========================================
# TOP ASESORES
# ==========================================

def top_asesores():
    solicitudes = obtener_solicitudes()
    contador = Counter()
    for fila in solicitudes:
        asesor = fila.get("asesor")
        if asesor:
            contador[asesor] += 1
    top = contador.most_common(10)
    respuesta = "🏆 TOP ASESORES\n\n"
    for asesor, cantidad in top:
        respuesta += (
            f"• {asesor}: {cantidad}\n"
        )
    return respuesta


# ==========================================
# TOP RUTAS
# ==========================================

def top_rutas():
    solicitudes = obtener_solicitudes()
    contador = Counter()
    for fila in solicitudes:
        ruta = fila.get("ruta")
        if ruta:
            contador[ruta] += 1
    top = contador.most_common(10)
    respuesta = "🛣️ TOP RUTAS\n\n"
    for ruta, cantidad in top:
        respuesta += (
            f"• {ruta}: {cantidad}\n"
        )
    return respuesta


# ==========================================
# EFECTIVIDAD POR JEFATURA
# ==========================================

def efectividad_jefaturas():
    solicitudes = obtener_solicitudes()
    resumen = {}
    for fila in solicitudes:
        jefatura = fila.get("jefatura")
        if not jefatura:
            continue
        if jefatura not in resumen:
            resumen[jefatura] = {
                "total": 0,
                "productivas": 0
            }
        resumen[jefatura]["total"] += 1
        if fila.get("estatus") == "PRODUCTIVA":
            resumen[jefatura]["productivas"] += 1
    respuesta = "📈 EFECTIVIDAD POR JEFATURA\n\n"
    for jefatura, datos in resumen.items():
        total = datos["total"]
        prod = datos["productivas"]
        porcentaje = round(
            (prod / total) * 100,
            1
        ) if total > 0 else 0
        respuesta += (
            f"• {jefatura}: "
            f"{porcentaje}%\n"
        )
    return respuesta


# ==========================================
# INSIGHTS
# ==========================================

def generar_insights():
    solicitudes = obtener_solicitudes()

    if not solicitudes:
        return "No existen datos suficientes."

    total = len(solicitudes)

    abiertas = len([
        s for s in solicitudes
        if s.get("estatus")
        not in [
            "PRODUCTIVA",
            "IMPRODUCTIVA",
            "CERRADA"
        ]
    ])

    productivas = len([
        s for s in solicitudes
        if s.get("estatus")
        == "PRODUCTIVA"
    ])

    contador_jefaturas = Counter()

    for fila in solicitudes:
        jefatura = fila.get("jefatura")

        if jefatura:
            contador_jefaturas[jefatura] += 1

    top_jefatura = contador_jefaturas.most_common(1)

    if top_jefatura:
        nombre_jefatura = top_jefatura[0][0]
        cantidad_jefatura = top_jefatura[0][1]
    else:
        nombre_jefatura = "N/D"
        cantidad_jefatura = 0

    eficiencia = 0

    if total > 0:
        eficiencia = round(
            (productivas / total) * 100,
            1
        )

    return f"""
🤖 INSIGHTS TRADE

Solicitudes Totales:
{total}

Solicitudes Abiertas:
{abiertas}

Solicitudes Productivas:
{productivas}

Jefatura con mayor volumen:
{nombre_jefatura}

Solicitudes en esa jefatura:
{cantidad_jefatura}

Efectividad Operativa:
{eficiencia} %
"""


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

    if pregunta == "TOP ASESORES":
        return top_asesores()

    if pregunta == "TOP RUTAS":
        return top_rutas()

    if pregunta == "EFECTIVIDAD JEFATURAS" or pregunta == "EFECTIVIDAD":
        return efectividad_jefaturas()

    if pregunta == "INSIGHTS":
        return generar_insights()

    if pregunta == "ULTIMO FOLIO" or pregunta == "ÚLTIMO FOLIO":
        return consultar_ultimo_folio()

    if "FOLIO" in pregunta:
        partes = pregunta.split()

        for palabra in partes:
            if palabra.startswith("TRD"):
                return buscar_folio(palabra)

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
• TOP ASESORES
• TOP RUTAS
• EFECTIVIDAD JEFATURAS
• INSIGHTS
• ÚLTIMO FOLIO
• FOLIO TRD-XXXXXX
"""
