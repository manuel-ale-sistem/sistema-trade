from collections import Counter
from datetime import datetime
import re
import pandas as pd
import plotly.express as px
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
# MODELOS CON MAYOR INCIDENCIA
# ==========================================
def modelos_mayor_incidencia():
    detalles = (
        supabase
        .table("solicitud_detalle")
        .select("modelo")
        .execute()
        .data
    )
    if not detalles:
        return """
🚨 MODELOS CON MÁS INCIDENCIAS
No existen datos disponibles.
"""
    contador = Counter()
    for fila in detalles:
        modelo = fila.get("modelo")
        if modelo:
            contador[modelo] += 1
    top = contador.most_common(10)
    respuesta = (
        "🚨 MODELOS CON MÁS INCIDENCIAS\n\n"
    )
    for modelo, cantidad in top:
        respuesta += (
            f"• {modelo}: "
            f"{cantidad} incidencias\n"
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
# TOP USUARIOS CAPTURISTAS
# ==========================================
def top_usuarios():
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return """
👨‍💼 TOP USUARIOS
No existen datos disponibles.
"""
    contador = Counter()
    for fila in solicitudes:
        usuario = fila.get("usuario")
        if usuario:
            contador[usuario] += 1
    top = contador.most_common(10)
    respuesta = (
        "👨‍💼 TOP USUARIOS CAPTURISTAS\n\n"
    )
    for usuario, cantidad in top:
        respuesta += (
            f"• {usuario}: "
            f"{cantidad} solicitudes\n"
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
# SOLICITUDES CRÍTICAS
# ==========================================

def solicitudes_criticas():
    solicitudes = obtener_solicitudes()
    respuesta = (
        "🚨 SOLICITUDES CRÍTICAS\n\n"
    )
    encontradas = 0
    for fila in solicitudes:
        estatus = fila.get(
            "estatus",
            ""
        )
        if estatus in [
            "PRODUCTIVA",
            "IMPRODUCTIVA",
            "CERRADA"
        ]:
            continue
        fecha = fila.get(
            "fecha",
            ""
        )
        if not fecha:
            continue
        try:
            fecha_sol = datetime.strptime(
                fecha[:10],
                "%Y-%m-%d"
            )
            dias = (
                datetime.now()
                - fecha_sol
            ).days
            if dias >= 7:
                encontradas += 1
                respuesta += (
                    f"• {fila.get('folio')} "
                    f"| {fila.get('negocio', 'N/D')} "
                    f"| {dias} días\n"
                )
        except Exception:
            continue
    if encontradas == 0:
        return """
✅ ALERTAS OPERATIVAS
No existen solicitudes críticas.
Todas las solicitudes abiertas
tienen menos de 7 días.
"""
    respuesta += (
        f"\nTotal críticas: {encontradas}"
    )
    return respuesta


# ==========================================
# TENDENCIAS DE SOLICITUDES
# ==========================================
def tendencias_solicitudes():
    try:
        detalles = (
            supabase
            .table("solicitud_detalle")
            .select("tipo_solicitud")
            .execute()
            .data
        )
        if not detalles:
            return """
📈 TENDENCIAS
No existen datos suficientes.
"""
        contador = Counter()
        for fila in detalles:
            tipo = fila.get(
                "tipo_solicitud"
            )
            if tipo:
                contador[tipo] += 1
        top = contador.most_common(10)
        respuesta = (
            "📈 TENDENCIAS DE SOLICITUDES\n\n"
        )
        for tipo, cantidad in top:
            respuesta += (
                f"• {tipo}: "
                f"{cantidad} registros\n"
            )
        return respuesta
    except Exception as e:
        return (
            f"Error analizando tendencias: {e}"
        )


# ==========================================
# JEFATURA LIDER
# ==========================================
def jefatura_lider():
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return "No existen datos."
    contador = Counter()
    for fila in solicitudes:
        jefatura = fila.get(
            "jefatura"
        )
        if jefatura:
            contador[jefatura] += 1
    lider = contador.most_common(1)
    if not lider:
        return "No existen datos."
    nombre = lider[0][0]
    total = lider[0][1]
    return f"""
🏆 JEFATURA LÍDER
Jefatura:
{nombre}
Solicitudes:
{total}
"""


# ==========================================
# ASESOR LIDER
# ==========================================
def asesor_lider():
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return "No existen datos."
    contador = Counter()
    for fila in solicitudes:
        asesor = fila.get(
            "asesor"
        )
        if asesor:
            contador[asesor] += 1
    lider = contador.most_common(1)
    if not lider:
        return "No existen datos."
    nombre = lider[0][0]
    total = lider[0][1]
    return f"""
🏆 ASESOR LÍDER
Asesor:
{nombre}
Solicitudes:
{total}
"""


# ==========================================
# RUTA LIDER
# ==========================================
def ruta_lider():
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return "No existen datos."
    contador = Counter()
    for fila in solicitudes:
        ruta = fila.get(
            "ruta"
        )
        if ruta:
            contador[ruta] += 1
    lider = contador.most_common(1)
    if not lider:
        return "No existen datos."
    nombre = lider[0][0]
    total = lider[0][1]
    return f"""
🏆 RUTA LÍDER
Ruta:
{nombre}
Solicitudes:
{total}
"""


# ==========================================
# RANKING OPERATIVO
# ==========================================
def ranking_operativo():
    return f"""
📈 RANKING OPERATIVO
{jefatura_lider()}
{asesor_lider()}
{ruta_lider()}
"""


# ==========================================
# MODELO LÍDER
# ==========================================
def modelo_lider():
    detalles = (
        supabase
        .table("solicitud_detalle")
        .select("modelo")
        .execute()
        .data
    )
    if not detalles:
        return "N/D"
    contador = Counter()
    for fila in detalles:
        modelo = fila.get("modelo")
        if modelo:
            contador[modelo] += 1
    lider = contador.most_common(1)
    if not lider:
        return "N/D"
    return lider[0][0]


# ==========================================
# TOTAL CRÍTICAS
# ==========================================
def total_criticas():
    solicitudes = obtener_solicitudes()
    total = 0
    for fila in solicitudes:
        estatus = fila.get(
            "estatus",
            ""
        )
        if estatus in [
            "PRODUCTIVA",
            "IMPRODUCTIVA",
            "CERRADA"
        ]:
            continue
        fecha = fila.get(
            "fecha",
            ""
        )
        if not fecha:
            continue
        try:
            fecha_sol = datetime.strptime(
                fecha[:10],
                "%Y-%m-%d"
            )
            dias = (
                datetime.now()
                - fecha_sol
            ).days
            if dias >= 7:
                total += 1
        except Exception:
            pass
    return total


# ==========================================
# RESUMEN EJECUTIVO
# ==========================================
def resumen_ejecutivo():
    metricas = obtener_metricas()
    modelo = modelo_lider()
    criticas = total_criticas()
    solicitudes = obtener_solicitudes()
    total = len(solicitudes)
    productivas = metricas[
        "productivas"
    ]
    eficiencia = 0
    if total > 0:
        eficiencia = round(
            (
                productivas /
                total
            ) * 100,
            1
        )
    return f"""
🤖 RESUMEN EJECUTIVO TRADE
📋 Solicitudes Totales:
{metricas["total"]}
📂 Solicitudes Abiertas:
{metricas["abiertas"]}
🚨 Solicitudes Críticas:
{criticas}
✅ Productivas:
{metricas["productivas"]}
❌ Improductivas:
{metricas["improductivas"]}
📈 Efectividad:
{eficiencia}%
🏆 Modelo Líder:
{modelo}
{jefatura_lider()}
{asesor_lider()}
{ruta_lider()}
"""


# ==========================================
# ALERTAS INTELIGENTES
# ==========================================
def alertas_inteligentes():
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return """
🤖 ALERTAS INTELIGENTES
No existen datos suficientes.
"""
    alertas = []
    criticas = total_criticas()
    if criticas > 0:
        alertas.append(
            f"🚨 Existen {criticas} solicitudes "
            f"críticas con más de 7 días."
        )
    total = len(solicitudes)
    productivas = len([
        s
        for s in solicitudes
        if s.get("estatus")
        == "PRODUCTIVA"
    ])
    if total > 0:
        efectividad = round(
            (productivas / total) * 100,
            1
        )
        if efectividad < 70:
            alertas.append(
                f"⚠️ La efectividad general es "
                f"{efectividad}%."
            )
    contador = Counter()
    for fila in solicitudes:
        jefatura = fila.get(
            "jefatura"
        )
        if jefatura:
            contador[jefatura] += 1
    lider = contador.most_common(1)
    if lider:
        alertas.append(
            f"📊 La jefatura con mayor carga "
            f"es {lider[0][0]} "
            f"con {lider[0][1]} solicitudes."
        )
    if not alertas:
        return """
✅ ALERTAS INTELIGENTES
No se detectaron anomalías.
"""
    
    respuesta = "🤖 ALERTAS INTELIGENTES\n\n"
    for alerta in alertas:
        respuesta += f"{alerta}\n"
    return respuesta


# ==========================================
# ANALISTA TRADE IA
# ==========================================
def analista_trade():
    metricas = obtener_metricas()
    alertas = alertas_inteligentes()
    insights = generar_insights()
    ranking = ranking_operativo()
    return f"""
🤖 ANALISTA TRADE
========================
📊 RESUMEN
Solicitudes Totales:
{metricas["total"]}
Solicitudes Abiertas:
{metricas["abiertas"]}
✅ Productivas:
{metricas["productivas"]}
❌ Improductivas:
{metricas["improductivas"]}
========================
🚨 ALERTAS
{alertas}
========================
📈 INSIGHTS
{insights}
========================
🏆 RANKING
{ranking}
========================
✅ RECOMENDACIONES
• Revisar solicitudes críticas.
• Monitorear la jefatura con mayor carga.
• Dar seguimiento a solicitudes abiertas.
• Revisar modelos con mayor incidencia.
• Evaluar efectividad operativa periódicamente.
"""


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
# CONSULTAS DINÁMICAS INTELIGENTES
# ==========================================
def procesar_consulta_dinamica(pregunta):
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return None
    
    pregunta_limpia = re.sub(
        r"[^A-Z0-9ÁÉÍÓÚÑ ]",
        "",
        pregunta.upper()
    )
    
    campos_a_revisar = ["jefatura", "ruta", "canal", "gec", "asesor", "usuario"]
    palabras_ignorar = {"CUANTAS", "SOLICITUDES", "TIENE", "EL", "LA", "LOS", "LAS", "DE", "DEL", "EN", "UN", "UNA", "CANAL", "RUTA", "JEFATURA"}
    tokens = [p for p in pregunta_limpia.split() if p not in palabras_ignorar]
    
    termino_busqueda = " ".join(tokens)
    if not termino_busqueda:
        return None

    for campo in campos_a_revisar:
        resultados = []
        for fila in solicitudes:
            valor_campo = str(fila.get(campo, "")).upper()
            if termino_busqueda in valor_campo or any(t in valor_campo for t in tokens):
                if "PRODUCTIVA" in pregunta and fila.get("estatus") != "PRODUCTIVA":
                    continue
                resultados.append(fila)
        
        if resultados:
            tipo_etiqueta = campo.upper()
            folios = [
                str(r.get("folio"))
                for r in resultados[:5]
                if r.get("folio")
            ]
            folios_texto = "\n".join([f"• {f}" for f in folios]) if folios else "• N/D"

            return f"""
📊 CONSULTA DINÁMICA
Campo:
{tipo_etiqueta}
Término:
{termino_busqueda.title()}
Total Solicitudes:
{len(resultados)}
Folios ejemplo:
{folios_texto}
"""
    return None
    # ==========================================
# DETALLE OPERATIVO
# ==========================================
def detalle_operativo(pregunta):
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return None
    campos = [
        "jefatura",
        "ruta",
        "canal",
        "gec",
        "asesor",
        "usuario"
    ]
    pregunta = pregunta.upper()
    resultados = []
    for campo in campos:
        valores = set()
        for fila in solicitudes:
            valor = fila.get(campo)
            if valor:
                valores.add(
                    str(valor).upper()
                )
        for valor in valores:
            if valor in pregunta:
                for fila in solicitudes:
                    dato = str(
                        fila.get(campo, "")
                    ).upper()
                    if valor not in dato:
                        continue
                    if (
                        "ABIERTA" in pregunta
                        or
                        "ABIERTAS" in pregunta
                    ):
                        if fila.get(
                            "estatus"
                        ) in [
                            "PRODUCTIVA",
                            "IMPRODUCTIVA",
                            "CERRADA"
                        ]:
                            continue
                    resultados.append(
                        fila
                    )
                break
    if not resultados:
        return None
    
    resultados = sorted(
        resultados,
        key=lambda x: str(
            x.get("fecha", "")
        ),
        reverse=True
    )
    
    respuesta = (
        "📋 DETALLE OPERATIVO\n\n"
    )
    respuesta += (
        f"Registros encontrados: "
        f"{len(resultados)}\n\n"
    )
    for fila in resultados[:20]:
        respuesta += (
            f"• {fila.get('folio')}\n"
            f"  Estatus: "
            f"{fila.get('estatus')}\n"
            f"  Negocio: "
            f"{fila.get('negocio')}\n\n"
        )
    if len(resultados) > 20:
        respuesta += (
            f"... y "
            f"{len(resultados) - 20} "
            f"más"
        )
    return respuesta


# ==========================================
# EXPORTACIÓN DE DATOS (LÓGICA DE NEGOCIO)
# ==========================================
def obtener_datos_exportacion(pregunta):
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return None
    pregunta = pregunta.upper()
    campos = [
        "jefatura",
        "ruta",
        "canal",
        "gec",
        "asesor",
        "usuario"
    ]
    resultados = []
    for campo in campos:
        valores = set()
        for fila in solicitudes:
            valor = fila.get(campo)
            if valor:
                valores.add(
                    str(valor).upper()
                )
        for valor in valores:
            if valor in pregunta:
                for fila in solicitudes:
                    dato = str(
                        fila.get(campo, "")
                    ).upper()
                    if valor not in dato:
                        continue
                    if "ABIERTA" in pregunta or "ABIERTAS" in pregunta:
                        if fila.get("estatus") in [
                            "PRODUCTIVA",
                            "IMPRODUCTIVA",
                            "CERRADA"
                        ]:
                            continue
                    if "PRODUCTIVA" in pregunta:
                        if fila.get("estatus") != "PRODUCTIVA":
                            continue
                    resultados.append(fila)
                break
    if not resultados:
        return None
    
    df = pd.DataFrame(resultados)
    nombre_archivo = (
        f"reporte_trade_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )
    df.to_excel(nombre_archivo, index=False)
    
    return {
        "archivo": nombre_archivo,
        "registros": len(df)
    }


# ==========================================
# GRAFICA JEFATURAS
# ==========================================
def grafica_jefaturas():
    solicitudes = obtener_solicitudes()
    contador = Counter()
    for fila in solicitudes:
        jefatura = fila.get("jefatura")
        if jefatura:
            contador[jefatura] += 1
    df = pd.DataFrame(
        contador.items(),
        columns=[
            "Jefatura",
            "Solicitudes"
        ]
    )
    fig = px.bar(
        df,
        x="Jefatura",
        y="Solicitudes",
        title="Solicitudes por Jefatura"
    )
    return fig


# ==========================================
# GRAFICA CANALES
# ==========================================
def grafica_canales():
    solicitudes = obtener_solicitudes()
    contador = Counter()
    for fila in solicitudes:
        canal = fila.get("canal")
        if canal:
            contador[canal] += 1
    df = pd.DataFrame(
        contador.items(),
        columns=[
            "Canal",
            "Solicitudes"
        ]
    )
    fig = px.pie(
        df,
        names="Canal",
        values="Solicitudes",
        title="Distribución por Canal"
    )
    return fig


# ==========================================
# GRAFICA MODELOS
# ==========================================
def grafica_modelos():
    detalles = (
        supabase
        .table("solicitud_detalle")
        .select("modelo")
        .execute()
        .data
    )
    if not detalles:
        return None
    contador = Counter()
    for fila in detalles:
        modelo = fila.get("modelo")
        if modelo:
            contador[modelo] += 1
    df = pd.DataFrame(
        contador.items(),
        columns=[
            "Modelo",
            "Total"
        ]
    )
    fig = px.bar(
        df,
        x="Modelo",
        y="Total",
        title="Top Modelos"
    )
    return fig


# ==========================================
# COMPARATIVO INTELIGENTE
# ==========================================
def comparativo_inteligente(pregunta):
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return """
📊 COMPARATIVO
No existen datos suficientes.
"""
    pregunta = pregunta.upper()
    campos = [
        "jefatura",
        "ruta",
        "canal",
        "asesor"
    ]
    for campo in campos:
        valores = list({
            str(
                fila.get(campo, "")
            ).upper()
            for fila in solicitudes
            if fila.get(campo)
        })
        encontrados = []
        for valor in valores:
            if valor in pregunta:
                encontrados.append(valor)
        if len(encontrados) >= 2:
            valor1 = encontrados[0]
            valor2 = encontrados[1]
            total1 = len([
                s for s in solicitudes
                if str(
                    s.get(campo, "")
                ).upper() == valor1
            ])
            total2 = len([
                s for s in solicitudes
                if str(
                    s.get(campo, "")
                ).upper() == valor2
            ])
            productivas1 = len([
                s for s in solicitudes
                if (
                    str(
                        s.get(campo, "")
                    ).upper() == valor1
                    and
                    s.get("estatus")
                    == "PRODUCTIVA"
                )
            ])
            productivas2 = len([
                s for s in solicitudes
                if (
                    str(
                        s.get(campo, "")
                    ).upper() == valor2
                    and
                    s.get("estatus")
                    == "PRODUCTIVA"
                )
            ])
            abiertas1 = len([
                s for s in solicitudes
                if (
                    str(
                        s.get(campo, "")
                    ).upper() == valor1
                    and
                    s.get("estatus")
                    not in [
                        "PRODUCTIVA",
                        "IMPRODUCTIVA",
                        "CERRADA"
                    ]
                )
            ])
            abiertas2 = len([
                s for s in solicitudes
                if (
                    str(
                        s.get(campo, "")
                    ).upper() == valor2
                    and
                    s.get("estatus")
                    not in [
                        "PRODUCTIVA",
                        "IMPRODUCTIVA",
                        "CERRADA"
                    ]
                )
            ])
            efectividad1 = round(
                (
                    productivas1 / total1
                ) * 100,
                1
            ) if total1 > 0 else 0
            efectividad2 = round(
                (
                    productivas2 / total2
                ) * 100,
                1
            ) if total2 > 0 else 0
            mejor = (
                valor1
                if efectividad1 >= efectividad2
                else valor2
            )
            return f"""
📊 COMPARATIVO INTELIGENTE
Campo:
{campo.upper()}
━━━━━━━━━━━━━━
{valor1}
• Solicitudes:
{total1}
• Productivas:
{productivas1}
• Abiertas:
{abiertas1}
• Efectividad:
{efectividad1}%
━━━━━━━━━━━━━━
{valor2}
• Solicitudes:
{total2}
• Productivas:
{productivas2}
• Abiertas:
{abiertas2}
• Efectividad:
{efectividad2}%
━━━━━━━━━━━━━━
🏆 Mejor desempeño:
{mejor}
"""
    return """
📊 COMPARATIVO
No encontré dos elementos
válidos para comparar.
Ejemplos:
• Cuernavaca vs Cuautla
• Six vs Tradicional
• Ruta 5 vs Ruta 8
"""


# ==========================================
# GRAFICA COMPARATIVO
# ==========================================
def grafica_comparativo(
    valor1,
    valor2,
    campo
):
    solicitudes = obtener_solicitudes()
    total1 = len([
        s
        for s in solicitudes
        if str(
            s.get(campo, "")
        ).upper() == valor1.upper()
    ])
    total2 = len([
        s
        for s in solicitudes
        if str(
            s.get(campo, "")
        ).upper() == valor2.upper()
    ])
    df = pd.DataFrame({
        campo: [
            valor1,
            valor2
        ],
        "Solicitudes": [
            total1,
            total2
        ]
    })
    fig = px.bar(
        df,
        x=campo,
        y="Solicitudes",
        color=campo,
        title=f"{valor1} vs {valor2}"
    )
    return fig


# ==========================================
# RIESGO OPERATIVO
# ==========================================
def riesgo_operativo():
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return """
🚨 RIESGO OPERATIVO
No existen datos suficientes.
"""
    resumen = {}
    for fila in solicitudes:
        jefatura = fila.get("jefatura")
        if not jefatura:
            continue
        if jefatura not in resumen:
            resumen[jefatura] = {
                "total": 0,
                "abiertas": 0,
                "criticas": 0,
                "productivas": 0
            }
        resumen[jefatura]["total"] += 1
        estatus = fila.get(
            "estatus",
            ""
        )
        if estatus == "PRODUCTIVA":
            resumen[jefatura][
                "productivas"
            ] += 1
        if estatus not in [
            "PRODUCTIVA",
            "IMPRODUCTIVA",
            "CERRADA"
        ]:
            resumen[jefatura][
                "abiertas"
            ] += 1
            try:
                fecha = fila.get(
                    "fecha",
                    ""
                )
                if fecha:
                    dias = (
                        datetime.now()
                        -
                        datetime.strptime(
                            fecha[:10],
                            "%Y-%m-%d"
                        )
                    ).days
                    if dias >= 7:
                        resumen[jefatura][
                            "criticas"
                        ] += 1
            except Exception:
                pass
    respuesta = (
        "🚨 RIESGO OPERATIVO\n\n"
    )
    ranking = []
    for jefatura, datos in resumen.items():
        total = datos["total"]
        efectividad = round(
            (
                datos["productivas"]
                / total
            ) * 100,
            1
        ) if total else 0
        score = (
            datos["abiertas"]
            +
            (datos["criticas"] * 2)
        )
        if efectividad < 70:
            score += 5
        ranking.append(
            (
                score,
                jefatura,
                efectividad,
                datos
            )
        )
    ranking.sort(
        reverse=True
    )
    for (
        score,
        jefatura,
        efectividad,
        datos
    ) in ranking[:5]:
        if score >= 15:
            nivel = "🔴 ALTO"
        elif score >= 8:
            nivel = "🟠 MEDIO"
        else:
            nivel = "🟢 BAJO"
        respuesta += f"""
{jefatura}
Riesgo:
{nivel}
• Abiertas:
{datos["abiertas"]}
• Críticas:
{datos["criticas"]}
• Efectividad:
{efectividad}%
---------------------
"""
    return respuesta


# ==========================================
# DIAGNÓSTICO EJECUTIVO
# ==========================================
def diagnostico_ejecutivo():
    metricas = obtener_metricas()
    total = metricas["total"]
    productivas = metricas[
        "productivas"
    ]
    efectividad = round(
        (
            productivas / total
        ) * 100,
        1
    ) if total else 0
    criticas = total_criticas()
    lider = jefatura_lider()
    diagnostico = f"""
🤖 DIAGNÓSTICO EJECUTIVO
📊 Situación General
Solicitudes:
{total}
Abiertas:
{metricas["abiertas"]}
Críticas:
{criticas}
Efectividad:
{efectividad}%
🏆 Liderazgo Operativo
{lider}
"""
    if criticas > 10:
        diagnostico += """
🚨 Observación
Existe acumulación importante
de solicitudes críticas.
Se recomienda priorizar
atención inmediata.
"""
    elif criticas > 0:
        diagnostico += """
⚠️ Observación
Existen solicitudes críticas
que deben monitorearse.
"""
    else:
        diagnostico += """
✅ Observación
No se detectan atrasos
operativos importantes.
"""
    if efectividad < 70:
        diagnostico += """
📉 Riesgo
La efectividad se encuentra
por debajo del objetivo.
"""
    else:
        diagnostico += """
📈 Desempeño
La efectividad es favorable.
"""
    
    diagnostico += f"""
========================
🚨 RIESGO OPERATIVO
{riesgo_operativo()}
"""
    return diagnostico


# ==========================================
# CENTRO EJECUTIVO
# ==========================================
def centro_ejecutivo():
    metricas = obtener_metricas()
    criticas = total_criticas()
    total = metricas["total"]
    productivas = metricas["productivas"]
    efectividad = round(
        (
            productivas / total
        ) * 100,
        1
    ) if total else 0
    return f"""
🏢 CENTRO EJECUTIVO TRADE
================================
📊 KPIS
Solicitudes Totales:
{metricas["total"]}
Solicitudes Abiertas:
{metricas["abiertas"]}
Solicitudes Productivas:
{metricas["productivas"]}
Solicitudes Improductivas:
{metricas["improductivas"]}
Solicitudes Críticas:
{criticas}
Efectividad Global:
{efectividad}%
================================
🚨 ALERTAS INTELIGENTES
{alertas_inteligentes()}
================================
⚠️ RIESGO OPERATIVO
{riesgo_operativo()}
================================
📋 DIAGNÓSTICO EJECUTIVO
{diagnostico_ejecutivo()}
================================
🏆 RANKING OPERATIVO
{ranking_operativo()}
================================
📈 TENDENCIAS
{tendencias_solicitudes()}
================================
🤖 INSIGHTS
{generar_insights()}
================================
✅ RECOMENDACIONES
• Revisar solicitudes críticas.
• Atender jefaturas con riesgo ALTO.
• Reducir solicitudes abiertas.
• Monitorear diariamente la efectividad.
• Revisar modelos con mayor incidencia.
• Dar seguimiento a tendencias.
================================
✅ FIN DEL REPORTE EJECUTIVO
"""


# ==========================================
# DASHBOARD EJECUTIVO
# ==========================================
def dashboard_ejecutivo():
    metricas = obtener_metricas()
    return {
        "total": metricas["total"],
        "abiertas": metricas["abiertas"],
        "productivas": metricas["productivas"],
        "improductivas": metricas["improductivas"],
        "criticas": total_criticas()
    }


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

    if any(
        x in pregunta
        for x in [
            "INCIDENCIA",
            "INCIDENCIAS"
        ]
    ):
        return modelos_mayor_incidencia()

    if pregunta == "TOP JEFATURAS":
        return top_jefaturas()

    if pregunta == "TOP CANALES":
        return top_canales()

    if pregunta == "TOP GEC":
        return top_gec()

    if any(
        x in pregunta
        for x in [
            "ASESOR",
            "ASESORES"
        ]
    ):
        return top_asesores()

    if any(
        x in pregunta
        for x in [
            "RUTA",
            "RUTAS"
        ]
    ) and "CUANTAS" not in pregunta:
        return top_rutas()

    if any(
        x in pregunta
        for x in [
            "USUARIO",
            "USUARIOS",
            "CAPTURA",
            "CAPTURAS",
            "CAPTURISTA",
            "CAPTURISTAS"
        ]
    ):
        return top_usuarios()

    if any(
        x in pregunta
        for x in [
            "EFECTIVIDAD",
            "POR JEFATURA",
            "DESEMPEÑO"
        ]
    ):
        return efectividad_jefaturas()

    if any(
        x in pregunta
        for x in [
            "CRITICA",
            "CRITICAS",
            "CRÍTICA",
            "CRÍTICAS",
            "ALERTA",
            "ALERTAS",
            "ATRASADA",
            "ATRASADAS",
            "PENDIENTE",
            "PENDIENTES"
        ]
    ):
        return solicitudes_criticas()

    if any(
        x in pregunta
        for x in [
            "TENDENCIA",
            "TENDENCIAS",
            "CRECIMIENTO",
            "AUMENTANDO",
            "SOLICITUDES MAS FRECUENTES",
            "SOLICITUDES MÁS FRECUENTES"
        ]
    ):
        return tendencias_solicitudes()

    if any(
        x in pregunta
        for x in [
            "RANKING",
            "LIDER",
            "LÍDER",
            "DESEMPEÑO GENERAL"
        ]
    ):
        return ranking_operativo()

    if any(
        x in pregunta
        for x in [
            "EJECUTIVO",
            "RESUMEN EJECUTIVO",
            "DASHBOARD EJECUTIVO"
        ]
    ):
        return resumen_ejecutivo()

    # ==========================================
    # CENTRO EJECUTIVO
    # ==========================================
    if any(
        x in pregunta
        for x in [
            "CENTRO EJECUTIVO",
            "TABLERO EJECUTIVO",
            "REPORTE EJECUTIVO",
            "ESTATUS GENERAL"
        ]
    ):
        return centro_ejecutivo()

    if any(
        x in pregunta
        for x in [
            "ALERTA INTELIGENTE",
            "ALERTAS INTELIGENTES",
            "ANOMALIAS",
            "ANOMALÍAS",
            "MONITOREO"
        ]
    ):
        return alertas_inteligentes()

    # ==========================================
    # COMPARATIVOS
    # ==========================================
    if (
        "VS" in pregunta
        or
        "COMPARA" in pregunta
        or
        "COMPARAR" in pregunta
    ):
        return comparativo_inteligente(
            pregunta
        )

    # ==========================================
    # RIESGO OPERATIVO
    # ==========================================
    if any(
        x in pregunta
        for x in [
            "RIESGO",
            "RIESGOS",
            "RIESGO OPERATIVO"
        ]
    ):
        return riesgo_operativo()

    # ==========================================
    # DIAGNOSTICO
    # ==========================================
    if any(
        x in pregunta
        for x in [
            "DIAGNOSTICO",
            "DIAGNÓSTICO",
            "DIAGNOSTICO EJECUTIVO",
            "ESTADO OPERATIVO"
        ]
    ):
        return diagnostico_ejecutivo()

    # ==========================================
    # ANALISTA TRADE
    # ==========================================
    if any(
        x in pregunta
        for x in [
            "ANALISIS",
            "ANÁLISIS",
            "ANALISTA",
            "OPERACION",
            "OPERACIÓN",
            "QUE ESTA PASANDO",
            "QUÉ ESTÁ PASANDO",
            "QUE DEBO REVISAR",
            "QUÉ DEBO REVISAR"
        ]
    ):
        return analista_trade()

    # ==========================================
    # INSIGHTS
    # ==========================================
    if pregunta == "INSIGHTS":
        return generar_insights()

    # ==========================================
    # ÚLTIMO FOLIO
    # ==========================================
    if (
        pregunta == "ULTIMO FOLIO"
        or
        pregunta == "ÚLTIMO FOLIO"
    ):
        return consultar_ultimo_folio()

    # ==========================================
    # BUSCAR FOLIO
    # ==========================================
    if "FOLIO" in pregunta:
        partes = pregunta.split()
        for palabra in partes:
            if "TRD" in palabra:
                return buscar_folio(
                    palabra
                )

    # ==========================================
    # EXPORTACIÓN
    # ==========================================
    if any(
        x in pregunta
        for x in [
            "EXPORTA",
            "EXPORTAR",
            "REPORTE",
            "EXCEL"
        ]
    ):
        resultado_exp = obtener_datos_exportacion(pregunta)
        if not resultado_exp:
            return "No se encontraron datos para exportar."
        return f"""
📁 REPORTE EXCEL GENERADO
Archivo:
{resultado_exp["archivo"]}
Total de registros:
{resultado_exp["registros"]}
"""

    # ==========================================
    # DETALLE OPERATIVO
    # ==========================================
    if any(
        x in pregunta
        for x in [
            "MOSTRAR",
            "MUESTRA",
            "MUESTRAME",
            "MUÉSTRAME",
            "DETALLE",
            "FOLIOS"
        ]
    ):
        detalle = detalle_operativo(
            pregunta
        )
        if detalle:
            return detalle

    resultado_dinamico = procesar_consulta_dinamica(pregunta)
    if resultado_dinamico:
        return resultado_dinamico

    return """No comprendí tu consulta. 
Puedes escribir comandos como:
• RESUMEN
• CENTRO EJECUTIVO
• TABLERO EJECUTIVO
• REPORTE EJECUTIVO
• ESTATUS GENERAL
O consultar un folio directamente."""
