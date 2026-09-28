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


def obtener_metricas(solicitudes=None):
    if solicitudes is None:
        solicitudes = obtener_solicitudes()
        
    total = len(solicitudes)
    abiertas = 0
    productivas = 0
    improductivas = 0
    
    for s in solicitudes:
        estatus = s.get("estatus")
        if estatus == "PRODUCTIVA":
            productivas += 1
        elif estatus == "IMPRODUCTIVA":
            improductivas += 1
            
        if estatus not in ["PRODUCTIVA", "IMPRODUCTIVA", "CERRADA"]:
            abiertas += 1
            
    return {
        "total": total,
        "abiertas": abiertas,
        "productivas": productivas,
        "improductivas": improductivas
    }


def ultimos_folios():
    try:
        return (
            supabase
            .table("solicitudes")
            .select("folio,negocio,estatus")
            .order("fecha", desc=True)
            .limit(5)
            .execute()
            .data
        )
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
        metricas = obtener_metricas(solicitudes)

        return f"""
📊 RESUMEN TRADE

Solicitudes Totales:
{metricas["total"]}

Solicitudes Abiertas:
{metricas["abiertas"]}

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
        st.session_state["ultimo_folio_ai"] = folio

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
    folio = st.session_state.get("ultimo_folio_ai")
    if not folio:
        return """
No tengo un folio en contexto.
Primero consulta algo como:
FOLIO TRD-000001
"""
    return buscar_folio(folio)


# ==========================================
# ABIERTAS / PRODUCTIVAS / IMPRODUCTIVAS
# ==========================================

def solicitudes_abiertas():
    metricas = obtener_metricas()
    return f"""
📂 SOLICITUDES ABIERTAS

Total:
{metricas["abiertas"]}
"""


def solicitudes_productivas():
    metricas = obtener_metricas()
    return f"""
✅ PRODUCTIVAS

Total:
{metricas["productivas"]}
"""


def solicitudes_improductivas():
    metricas = obtener_metricas()
    return f"""
❌ IMPRODUCTIVAS

Total:
{metricas["improductivas"]}
"""


# ==========================================
# TOP MODELOS / INCIDENCIAS
# ==========================================

def _obtener_contador_detalles(campo="modelo", limite=10):
    try:
        detalles = (
            supabase
            .table("solicitud_detalle")
            .select(campo)
            .execute()
            .data
        )
        if not detalles:
            return Counter()
        contador = Counter()
        for fila in detalles:
            valor = fila.get(campo)
            if valor:
                contador[valor] += 1
        return contador
    except Exception:
        return Counter()


def top_modelos():
    contador = _obtener_contador_detalles("modelo")
    if not contador:
        return "🏆 TOP MODELOS\n\nNo existen datos disponibles."
    
    respuesta = "🏆 TOP MODELOS\n\n"
    for modelo, cantidad in contador.most_common(10):
        respuesta += f"• {modelo}: {cantidad}\n"
    return respuesta


def modelos_mayor_incidencia():
    contador = _obtener_contador_detalles("modelo")
    if not contador:
        return """
🚨 MODELOS COM MÁS INCIDENCIAS
No existen datos disponibles.
"""
    respuesta = "🚨 MODELOS CON MÁS INCIDENCIAS\n\n"
    for modelo, cantidad in contador.most_common(10):
        respuesta += f"• {modelo}: {cantidad} incidencias\n"
    return respuesta


# ==========================================
# TOPS GENERALES (JEFATURAS, CANALES, GEC, ASESORES, RUTAS, USUARIOS)
# ==========================================

def _obtener_contador_solicitudes(solicitudes, campo):
    contador = Counter()
    for fila in solicitudes:
        valor = fila.get(campo)
        if valor:
            contador[valor] += 1
    return contador


def top_jefaturas():
    solicitudes = obtener_solicitudes()
    contador = _obtener_contador_solicitudes(solicitudes, "jefatura")
    respuesta = "🏆 TOP JEFATURAS\n\n"
    for nombre, cantidad in contador.most_common(10):
        respuesta += f"• {nombre}: {cantidad}\n"
    return respuesta


def top_canales():
    solicitudes = obtener_solicitudes()
    contador = _obtener_contador_solicitudes(solicitudes, "canal")
    respuesta = "🏆 TOP CANALES\n\n"
    for nombre, cantidad in contador.most_common(10):
        respuesta += f"• {nombre}: {cantidad}\n"
    return respuesta


def top_gec():
    solicitudes = obtener_solicitudes()
    contador = _obtener_contador_solicitudes(solicitudes, "gec")
    respuesta = "🏆 TOP GEC\n\n"
    for nombre, cantidad in contador.most_common(10):
        respuesta += f"• {nombre}: {cantidad}\n"
    return respuesta


def top_asesores():
    solicitudes = obtener_solicitudes()
    contador = _obtener_contador_solicitudes(solicitudes, "asesor")
    respuesta = "🏆 TOP ASESORES\n\n"
    for asesor, cantidad in contador.most_common(10):
        respuesta += f"• {asesor}: {cantidad}\n"
    return respuesta


def top_rutas():
    solicitudes = obtener_solicitudes()
    contador = _obtener_contador_solicitudes(solicitudes, "ruta")
    respuesta = "🛣️ TOP RUTAS\n\n"
    for ruta, cantidad in contador.most_common(10):
        respuesta += f"• {ruta}: {cantidad}\n"
    return respuesta


def top_usuarios():
    solicitudes = obtener_solicitudes()
    contador = _obtener_contador_solicitudes(solicitudes, "usuario")
    if not contador:
        return "\n👨‍💼 TOP USUARIOS\nNo existen datos disponibles.\n"
    
    respuesta = "👨‍💼 TOP USUARIOS CAPTURISTAS\n\n"
    for usuario, cantidad in contador.most_common(10):
        respuesta += f"• {usuario}: {cantidad} solicitudes\n"
    return respuesta


# ==========================================
# EFECTIVIDAD POR JEFATURA
# ==========================================

def efectividad_jefaturas(solicitudes=None):
    if solicitudes is None:
        solicitudes = obtener_solicitudes()
        
    resumen = {}
    for fila in solicitudes:
        jefatura = fila.get("jefatura")
        if not jefatura:
            continue
        if jefatura not in resumen:
            resumen[jefatura] = {"total": 0, "productivas": 0}
        resumen[jefatura]["total"] += 1
        if fila.get("estatus") == "PRODUCTIVA":
            resumen[jefatura]["productivas"] += 1
            
    respuesta = "📈 EFECTIVIDAD POR JEFATURA\n\n"
    for jefatura, datos in resumen.items():
        total = datos["total"]
        prod = datos["productivas"]
        porcentaje = round((prod / total) * 100, 1) if total > 0 else 0
        respuesta += f"• {jefatura}: {porcentaje}%\n"
    return respuesta


# ==========================================
# SOLICITUDES CRÍTICAS Y TOTAL
# ==========================================

def total_criticas(solicitudes=None):
    if solicitudes is None:
        solicitudes = obtener_solicitudes()
        
    total = 0
    hoy = datetime.now()
    estatus_excluidos = {"PRODUCTIVA", "IMPRODUCTIVA", "CERRADA"}
    
    for fila in solicitudes:
        if fila.get("estatus") in estatus_excluidos:
            continue
        fecha = fila.get("fecha")
        if not fecha:
            continue
        try:
            fecha_sol = datetime.strptime(fecha[:10], "%Y-%m-%d")
            dias = (hoy - fecha_sol).days
            if dias >= 7:
                total += 1
        except Exception:
            pass
    return total


def solicitudes_criticas(solicitudes=None):
    if solicitudes is None:
        solicitudes = obtener_solicitudes()
        
    respuesta = "🚨 SOLICITUDES CRÍTICAS\n\n"
    encontradas = 0
    hoy = datetime.now()
    estatus_excluidos = {"PRODUCTIVA", "IMPRODUCTIVA", "CERRADA"}
    
    for fila in solicitudes:
        if fila.get("estatus") in estatus_excluidos:
            continue
        fecha = fila.get("fecha")
        if not fecha:
            continue
        try:
            fecha_sol = datetime.strptime(fecha[:10], "%Y-%m-%d")
            dias = (hoy - fecha_sol).days
            if dias >= 7:
                encontradas += 1
                respuesta += f"• {fila.get('folio')} | {fila.get('negocio', 'N/D')} | {dias} días\n"
        except Exception:
            continue
            
    if encontradas == 0:
        return """
✅ ALERTAS OPERATIVAS
No existen solicitudes críticas.
Todas las solicitudes abiertas
tienen menos de 7 días.
"""
    respuesta += f"\nTotal críticas: {encontradas}"
    return respuesta


# ==========================================
# TENDENCIAS DE SOLICITUDES
# ==========================================

def tendencias_solicitudes():
    try:
        contador = _obtener_contador_detalles("tipo_solicitud")
        if not contador:
            return "\n📈 TENDENCIAS\nNo existen datos suficientes.\n"
            
        respuesta = "📈 TENDENCIAS DE SOLICITUDES\n\n"
        for tipo, cantidad in contador.most_common(10):
            respuesta += f"• {tipo}: {cantidad} registros\n"
        return respuesta
    except Exception as e:
        return f"Error analizando tendencias: {e}"


# ==========================================
# LÍDERES (JEFATURA, ASESOR, RUTA, MODELO)
# ==========================================

def jefatura_lider(solicitudes=None):
    if solicitudes is None:
        solicitudes = obtener_solicitudes()
    contador = _obtener_contador_solicitudes(solicitudes, "jefatura")
    lider = contador.most_common(1)
    if not lider:
        return "No existen datos."
    return f"""
🏆 JEFATURA LÍDER
Jefatura:
{lider[0][0]}
Solicitudes:
{lider[0][1]}
"""


def asesor_lider(solicitudes=None):
    if solicitudes is None:
        solicitudes = obtener_solicitudes()
    contador = _obtener_contador_solicitudes(solicitudes, "asesor")
    lider = contador.most_common(1)
    if not lider:
        return "No existen datos."
    return f"""
🏆 ASESOR LÍDER
Asesor:
{lider[0][0]}
Solicitudes:
{lider[0][1]}
"""


def ruta_lider(solicitudes=None):
    if solicitudes is None:
        solicitudes = obtener_solicitudes()
    contador = _obtener_contador_solicitudes(solicitudes, "ruta")
    lider = contador.most_common(1)
    if not lider:
        return "No existen datos."
    return f"""
🏆 RUTA LÍDER
Ruta:
{lider[0][0]}
Solicitudes:
{lider[0][1]}
"""


def ranking_operativo():
    solicitudes = obtener_solicitudes()
    return f"""
📈 RANKING OPERATIVO
{jefatura_lider(solicitudes)}
{asesor_lider(solicitudes)}
{ruta_lider(solicitudes)}
"""


def modelo_lider():
    contador = _obtener_contador_detalles("modelo")
    lider = contador.most_common(1)
    return lider[0][0] if lider else "N/D"


# ==========================================
# PRIORIDADES, RESUMEN EJECUTIVO Y ALERTAS
# ==========================================

def prioridades_del_dia():
    solicitudes = obtener_solicitudes()
    criticas = total_criticas(solicitudes)
    metricas = obtener_metricas(solicitudes)
    return f"""
📋 PRIORIDADES DEL DÍA
• Solicitudes críticas a revisar: {criticas}
• Solicitudes abiertas totales: {metricas["abiertas"]}
• Monitorear jefaturas con mayor carga de trabajo.
• Validar estatus de pendientes operativos.
"""


def resumen_ejecutivo():
    solicitudes = obtener_solicitudes()
    metricas = obtener_metricas(solicitudes)
    modelo = modelo_lider()
    criticas = total_criticas(solicitudes)
    total = metricas["total"]
    productivas = metricas["productivas"]
    
    eficiencia = round((productivas / total) * 100, 1) if total > 0 else 0
    
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
{jefatura_lider(solicitudes)}
{asesor_lider(solicitudes)}
{ruta_lider(solicitudes)}
"""


def alertas_inteligentes():
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return """
🤖 ALERTAS INTELIGENTES
No existen datos suficientes.
"""
    alertas = []
    criticas = total_criticas(solicitudes)
    if criticas > 0:
        alertas.append(f"🚨 Existen {criticas} solicitudes críticas con más de 7 días.")
        
    metricas = obtener_metricas(solicitudes)
    total = metricas["total"]
    productivas = metricas["productivas"]
    
    if total > 0:
        efectividad = round((productivas / total) * 100, 1)
        if efectividad < 70:
            alertas.append(f"⚠️ La efectividad general es {efectividad}%.") # Corregido
            
    contador = _obtener_contador_solicitudes(solicitudes, "jefatura")
    lider = contador.most_common(1)
    if lider:
        alertas.append(f"📊 La jefatura con mayor carga es {lider[0][0]} con {lider[0][1]} solicitudes.")
        
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
# CENTRO EJECUTIVO Y AYUDA
# ==========================================

def centro_ejecutivo():
    solicitudes = obtener_solicitudes()
    metricas = obtener_metricas(solicitudes)
    insights = generar_insights() # Asegúrate de tener esta función en tu módulo complementario
    return f"""
🤖 CENTRO EJECUTIVO
================================
📊 MÉTRICAS GENERALES
Totales: {metricas["total"]}
Abiertas: {metricas["abiertas"]}
Productivas: {metricas["productivas"]}
Improductivas: {metricas["improductivas"]}
================================
🤖 INSIGHTS
{insights}
================================
📋 PRIORIDADES DEL DÍA
{prioridades_del_dia()}
"""


def ayuda_final():
    return """
💡 COMANDOS DISPONIBLES:
RESUMEN GENERAL
ESTATUS DE FOLIO [FOLIO]
SOLICITUDES ABIERTAS
PRODUCTIVAS
IMPRODUCTIVAS
TOP MODELOS
TOP JEFATURAS
TOP CANALES
TOP GEC
TOP ASESORES
TOP RUTAS
TOP USUARIOS
EFECTIVIDAD
CRITICAS
TENDENCIAS
RANKING
RESUMEN EJECUTIVO
ALERTAS
CENTRO EJECUTIVO
PRIORIDADES
• PRIORIDADES DEL DIA
• ¿QUE DEBO REVISAR HOY?
• ¿QUE ES URGENTE?
"""
    from collections import Counter
from datetime import datetime
import pandas as pd
import plotly.express as px

# ==========================================
# UTILIDAD PRIVADA: ANÁLISIS DE JEFATURAS (CACHÉ INTERNA)
# ==========================================
def _calcular_resumen_jefaturas(solicitudes):
    """Calcula métricas por jefatura en una sola pasada para evitar bucles múltiples."""
    resumen = {}
    hoy = datetime.now()
    
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
        estatus = fila.get("estatus", "")
        
        if estatus == "PRODUCTIVA":
            resumen[jefatura]["productivas"] += 1
            
        if estatus not in ["PRODUCTIVA", "IMPRODUCTIVA", "CERRADA"]:
            resumen[jefatura]["abiertas"] += 1
            fecha = fila.get("fecha", "")
            if fecha:
                try:
                    dias = (hoy - datetime.strptime(fecha[:10], "%Y-%m-%d")).days
                    if dias >= 7:
                        resumen[jefatura]["criticas"] += 1
                except Exception:
                    pass
                    
    return resumen


# ==========================================
# GRAFICA JEFATURAS
# ==========================================
def grafica_jefaturas():
    solicitudes = obtener_solicitudes()
    contador = Counter(fila.get("jefatura") for fila in solicitudes if fila.get("jefatura"))
    
    df = pd.DataFrame(contador.items(), columns=["Jefatura", "Solicitudes"])
    fig = px.bar(df, x="Jefatura", y="Solicitudes", title="Solicitudes por Jefatura")
    return fig


# ==========================================
# GRAFICA CANALES
# ==========================================
def grafica_canales():
    solicitudes = obtener_solicitudes()
    contador = Counter(fila.get("canal") for fila in solicitudes if fila.get("canal"))
    
    df = pd.DataFrame(contador.items(), columns=["Canal", "Solicitudes"])
    fig = px.pie(df, names="Canal", values="Solicitudes", title="Distribución por Canal")
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
        
    contador = Counter(fila.get("modelo") for fila in detalles if fila.get("modelo"))
    df = pd.DataFrame(contador.items(), columns=["Modelo", "Total"])
    fig = px.bar(df, x="Modelo", y="Total", title="Top Modelos")
    return fig


# ==========================================
# COMPARATIVO INTELIGENTE
# ==========================================
def comparativo_inteligente(pregunta):
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return "\n📊 COMPARATIVO\nNo existen datos suficientes.\n"
        
    pregunta = pregunta.upper()
    campos = ["jefatura", "ruta", "canal", "asesor"]
    
    for campo in campos:
        valores = list({str(fila.get(campo, "")).upper() for fila in solicitudes if fila.get(campo)})
        encontrados = [valor for valor in valores if valor in pregunta]
        
        if len(encontrados) >= 2:
            valor1, valor2 = encontrados[0], encontrados[1]
            
            total1 = total2 = productivas1 = productivas2 = abiertas1 = abiertas2 = 0
            
            for s in solicitudes:
                val_campo = str(s.get(campo, "")).upper()
                estatus = s.get("estatus")
                is_prod = (estatus == "PRODUCTIVA")
                is_abierta = estatus not in ["PRODUCTIVA", "IMPRODUCTIVA", "CERRADA"]
                
                if val_campo == valor1:
                    total1 += 1
                    if is_prod: productivas1 += 1
                    if is_abierta: abiertas1 += 1
                elif val_campo == valor2:
                    total2 += 1
                    if is_prod: productivas2 += 1
                    if is_abierta: abiertas2 += 1
                    
            efectividad1 = round((productivas1 / total1) * 100, 1) if total1 > 0 else 0
            efectividad2 = round((productivas2 / total2) * 100, 1) if total2 > 0 else 0
            mejor = valor1 if efectividad1 >= efectividad2 else valor2
            
            return f"""
📊 COMPARATIVO INTELIGENTE
Campo: {campo.upper()}
━━━━━━━━━━━━━━
{valor1}
• Solicitudes: {total1}
• Productivas: {productivas1}
• Abiertas: {abiertas1}
• Efectividad: {efectividad1}%
━━━━━━━━━━━━━━
{valor2}
• Solicitudes: {total2}
• Productivas: {productivas2}
• Abiertas: {abiertas2}
• Efectividad: {efectividad2}%
━━━━━━━━━━━━━━
🏆 Mejor desempeño: {mejor}
"""
    return """
📊 COMPARATIVO
No encontré dos elementos válidos para comparar.
Ejemplos:
• Cuernavaca vs Cuautla
• Six vs Tradicional
• Ruta 5 vs Ruta 8
"""


# ==========================================
# GRAFICA COMPARATIVO
# ==========================================
def grafica_comparativo(valor1, valor2, campo):
    solicitudes = obtener_solicitudes()
    v1_up, v2_up = valor1.upper(), valor2.upper()
    
    total1 = sum(1 for s in solicitudes if str(s.get(campo, "")).upper() == v1_up)
    total2 = sum(1 for s in solicitudes if str(s.get(campo, "")).upper() == v2_up)
    
    df = pd.DataFrame({
        campo: [valor1, valor2],
        "Solicitudes": [total1, total2]
    })
    fig = px.bar(df, x=campo, y="Solicitudes", color=campo, title=f"{valor1} vs {valor2}")
    return fig


# ==========================================
# RIESGO OPERATIVO
# ==========================================
def riesgo_operativo(solicitudes=None):
    if solicitudes is None:
        solicitudes = obtener_solicitudes()
    if not solicitudes:
        return "\n🚨 RIESGO OPERATIVO\nNo existen datos suficientes.\n"
        
    resumen = _calcular_resumen_jefaturas(solicitudes)
    respuesta = "🚨 RIESGO OPERATIVO\n\n"
    ranking = []
    
    for jefatura, datos in resumen.items():
        total = datos["total"]
        efectividad = round((datos["productivas"] / total) * 100, 1) if total else 0
        score = datos["abiertas"] + (datos["criticas"] * 2)
        if efectividad < 70:
            score += 5
        ranking.append((score, jefatura, efectividad, datos))
        
    ranking.sort(reverse=True)
    
    for score, jefatura, efectividad, datos in ranking[:5]:
        if score >= 15:
            nivel = "🔴 ALTO"
        elif score >= 8:
            nivel = "🟠 MEDIO"
        else:
            nivel = "🟢 BAJO"
            
        respuesta += f"""
{jefatura}
Riesgo: {nivel}
• Abiertas: {datos["abiertas"]}
• Críticas: {datos["criticas"]}
• Efectividad: {efectividad}%
---------------------
"""
    return respuesta


# ==========================================
# PREDICCIÓN DE SATURACIÓN OPERATIVA
# ==========================================
def prediccion_saturacion(solicitudes=None):
    if solicitudes is None:
        solicitudes = obtener_solicitudes()
    if not solicitudes:
        return "\n🔮 PREDICCIÓN DE SATURACIÓN\nNo existen datos suficientes.\n"

    resumen = _calcular_resumen_jefaturas(solicitudes)
    respuesta = "🔮 PREDICCIÓN DE SATURACIÓN\n\n"
    ranking = []

    for jefatura, datos in resumen.items():
        total = datos["total"]
        efectividad = round((datos["productivas"] / total) * 100, 1) if total else 0
        score = datos["abiertas"] + (datos["criticas"] * 3)
        if efectividad < 70:
            score += 10

        if score >= 25:
            riesgo = "🔴 ALTO"
        elif score >= 12:
            riesgo = "🟠 MEDIO"
        else:
            riesgo = "🟢 BAJO"

        ranking.append((score, jefatura, riesgo, efectividad, datos))

    ranking.sort(reverse=True)

    for score, jefatura, riesgo, efectividad, datos in ranking[:10]:
        respuesta += f"""
📍 {jefatura}
Riesgo proyectado: {riesgo}
Abiertas: {datos['abiertas']}
Críticas: {datos['criticas']}
Efectividad: {efectividad}%
Score: {score}
------------------------
"""

    respuesta += "\n\n🤖 CONCLUSIÓN\nLas jefaturas con riesgo ALTO deben ser atendidas de forma prioritaria para evitar saturación operativa.\n"
    return respuesta


# ==========================================
# RECOMENDACIONES AUTOMÁTICAS
# ==========================================
def recomendaciones_automaticas():
    recomendaciones = []
    metricas = obtener_metricas()
    criticas = total_criticas()

    if criticas > 0:
        recomendaciones.append(f"🚨 Atender {criticas} solicitudes críticas.")

    if metricas["abiertas"] > 20:
        recomendaciones.append("📂 Reducir solicitudes abiertas.")

    solicitudes = obtener_solicitudes()
    resumen = _calcular_resumen_jefaturas(solicitudes)

    peor_jefatura = None
    peor_efectividad = 999

    for jefatura, datos in resumen.items():
        total = datos["total"]
        efectividad = (datos["productivas"] / total) * 100 if total else 0
        if efectividad < peor_efectividad:
            peor_efectividad = efectividad
            peor_jefatura = jefatura

    if peor_jefatura:
        recomendaciones.append(f"📉 Revisar efectividad de {peor_jefatura} ({round(peor_efectividad, 1)}%).")

    modelo_riesgo = modelo_lider()
    if modelo_riesgo != "N/D":
        recomendaciones.append(f"🧊 Monitorear incidencias del modelo {modelo_riesgo}.")

    if not recomendaciones:
        return "\n✅ RECOMENDACIONES\nNo existen acciones prioritarias.\n"

    respuesta = "🤖 RECOMENDACIONES AUTOMÁTICAS\n\n"
    for idx, rec in enumerate(recomendaciones, start=1):
        respuesta += f"{idx}. {rec}\n\n"

    return respuesta


# ==========================================
# PRIORIDADES DEL DÍA
# ==========================================
def prioridades_del_dia():
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return "\n📋 PRIORIDADES DEL DÍA\nNo existen datos suficientes.\n"

    prioridades = []
    criticas = []
    hoy = datetime.now()

    for fila in solicitudes:
        estatus = fila.get("estatus", "")
        if estatus in ["PRODUCTIVA", "IMPRODUCTIVA", "CERRADA"]:
            continue
        try:
            fecha = fila.get("fecha", "")
            if fecha:
                dias = (hoy - datetime.strptime(fecha[:10], "%Y-%m-%d")).days
                if dias >= 7:
                    criticas.append((fila.get("folio"), dias))
        except Exception:
            pass

    if criticas:
        prioridades.append(f"🚨 Solicitudes críticas: {len(criticas)}")

    metricas = obtener_metricas()
    if metricas["abiertas"] > 20:
        prioridades.append(f"📂 Solicitudes abiertas: {metricas['abiertas']}")

    riesgo = riesgo_operativo(solicitudes)
    if "🔴 ALTO" in riesgo:
        prioridades.append("⚠️ Existen jefaturas con riesgo ALTO.")

    modelo = modelo_lider()
    prioridades.append(f"🧊 Revisar incidencias del modelo {modelo}")

    respuesta = "📋 PRIORIDADES DEL DÍA\n\n"
    if not prioridades:
        respuesta += "✅ No existen prioridades urgentes."
        return respuesta

    for idx, item in enumerate(prioridades, start=1):
        respuesta += f"{idx}. {item}\n\n"

    if criticas:
        respuesta += "🚨 FOLIOS PRIORITARIOS\n\n"
        for folio, dias in criticas[:10]:
            respuesta += f"• {folio} ({dias} días)\n"

    return respuesta


# ==========================================
# DIAGNÓSTICO EJECUTIVO
# ==========================================
def diagnostico_ejecutivo():
    solicitudes = obtener_solicitudes()
    metricas = obtener_metricas()
    total = metricas["total"]
    productivas = metricas["productivas"]
    efectividad = round((productivas / total) * 100, 1) if total else 0
    criticas = total_criticas()
    lider = jefatura_lider()
    
    diagnostico = f"""
🤖 DIAGNÓSTICO EJECUTIVO
📊 Situación General
Solicitudes: {total}
Abiertas: {metricas["abiertas"]}
Críticas: {criticas}
Efectividad: {efectividad}%
🏆 Liderazgo Operativo
{lider}
"""
    if criticas > 10:
        diagnostico += "\n🚨 Observación\nExiste acumulación importante de solicitudes críticas.\nSe recomienda priorizar atención inmediata.\n"
    elif criticas > 0:
        diagnostico += "\n⚠️ Observación\nExisten solicitudes críticas que deben monitorearse.\n"
    else:
        diagnostico += "\n✅ Observación\nNo se detectan atrasos operativos importantes.\n"

    if efectividad < 70:
        diagnostico += "\n📉 Riesgo\nLa efectividad se encuentra por debajo del objetivo.\n"
    else:
        diagnostico += "\n📈 Desempeño\nLa efectividad es favorable.\n"

    diagnostico += f"\n========================\n🚨 RIESGO OPERATIVO\n{riesgo_operativo(solicitudes)}\n"
    return diagnostico


# ==========================================
# CENTRO EJECUTIVO
# ==========================================
def centro_ejecutivo():
    solicitudes = obtener_solicitudes()
    metricas = obtener_metricas()
    criticas = total_criticas()
    total = metricas["total"]
    productivas = metricas["productivas"]
    efectividad = round((productivas / total) * 100, 1) if total else 0
    
    return f"""
🏢 CENTRO EJECUTIVO TRADE
================================
📊 KPIS
Solicitudes Totales: {metricas["total"]}
Solicitudes Abiertas: {metricas["abiertas"]}
Solicitudes Productivas: {metricas["productivas"]}
Solicitudes Improductivas: {metricas["improductivas"]}
Solicitudes Críticas: {criticas}
Efectividad Global: {efectividad}%
================================
🚨 ALERTAS INTELIGENTES
{alertas_inteligentes()}
================================
⚠️ RIESGO OPERATIVO
{riesgo_operativo(solicitudes)}
================================
🔮 PREDICCIÓN DE SATURACIÓN
{prediccion_saturacion(solicitudes)}
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

    if any(x in pregunta for x in ["INCIDENCIA", "INCIDENCIAS"]):
        return modelos_mayor_incidencia()
    if pregunta == "TOP JEFATURAS":
        return top_jefaturas()
    if pregunta == "TOP CANALES":
        return top_canales()
    if pregunta == "TOP GEC":
        return top_gec()

    if any(x in pregunta for x in ["ASESOR", "ASESORES"]):
        return top_asesores()

    if any(x in pregunta for x in ["RUTA", "RUTAS"]) and "CUANTAS" not in pregunta:
        return top_rutas()

    if any(x in pregunta for x in ["USUARIO", "USUARIOS", "CAPTURA", "CAPTURAS", "CAPTURISTA", "CAPTURISTAS"]):
        return top_usuarios()

    if any(x in pregunta for x in ["EFECTIVIDAD", "POR JEFATURA", "DESEMPEÑO"]):
        return efectividad_jefaturas()

    if any(x in pregunta for x in ["CRITICA", "CRITICAS", "CRÍTICA", "CRÍTICAS", "ALERTA", "ALERTAS", "ATRASADA", "ATRASADAS", "PENDIENTE", "PENDIENTES"]):
        return solicitudes_criticas()

    if any(x in pregunta for x in ["TENDENCIA", "TENDENCIAS", "CRECIMIENTO", "AUMENTANDO", "SOLICITUDES MAS FRECUENTES", "SOLICITUDES MÁS FRECUENTES"]):
        return tendencias_solicitudes()

    if any(x in pregunta for x in ["RANKING", "LIDER", "LÍDER", "DESEMPEÑO GENERAL"]):
        return ranking_operativo()

    if any(x in pregunta for x in ["RESUMEN EJECUTIVO", "DASHBOARD EJECUTIVO"]):
        return resumen_ejecutivo()

    if any(x in pregunta for x in ["CENTRO EJECUTIVO", "TABLERO EJECUTIVO", "REPORTE EJECUTIVO", "ESTATUS GENERAL"]):
        return centro_ejecutivo()

    if any(x in pregunta for x in ["ALERTA INTELIGENTE", "ALERTAS INTELIGENTES", "ANOMALIAS", "ANOMALÍAS", "MONITOREO"]):
        return alertas_inteligentes()

    if any(x in pregunta for x in ["SATURACION", "SATURACIÓN", "PREDICCION", "PREDICCIÓN", "RIESGO FUTURO", "SATURACION OPERATIVA"]):
        return prediccion_saturacion()

    if "VS" in pregunta or "COMPARA" in pregunta or "COMPARAR" in pregunta:
        return comparativo_inteligente(pregunta)

    if any(x in pregunta for x in ["RIESGO", "RIESGOS", "RIESGO OPERATIVO"]):
        return riesgo_operativo()

    if any(x in pregunta for x in ["DIAGNOSTICO", "DIAGNÓSTICO", "DIAGNOSTICO EJECUTIVO", "ESTADO OPERATIVO"]):
        return diagnostico_ejecutivo()

    if any(x in pregunta for x in ["RECOMENDACION", "RECOMENDACIONES", "ACCIONES", "PRIORIDADES"]):
        return recomendaciones_automaticas()

    if any(x in pregunta for x in ["ANALISIS", "ANÁLISIS", "ANALISTA", "OPERACION", "OPERACIÓN", "QUE ESTA PASANDO", "QUÉ ESTÁ PASANDO", "QUE DEBO REVISAR", "QUÉ DEBO REVISAR"]):
        return analista_trade()

    if pregunta == "INSIGHTS":
        return generar_insights()

    if pregunta in ["ULTIMO FOLIO", "ÚLTIMO FOLIO"]:
        return consultar_ultimo_folio()

    if "FOLIO" in pregunta:
        for palabra in pregunta.split():
            if "TRD" in palabra:
                return buscar_folio(palabra)

    if any(x in pregunta for x in ["EXPORTA", "EXPORTAR", "REPORTE", "EXCEL"]):
        resultado_exp = obtener_datos_exportacion(pregunta)
        if not resultado_exp:
            return "No se encontraron datos para exportar."
        return f"""
📁 REPORTE EXCEL GENERADO
Archivo: {resultado_exp["archivo"]}
Total de registros: {resultado_exp["registros"]}
"""

    if any(x in pregunta for x in ["MOSTRAR", "MUESTRA", "MUESTRAME", "MUÉSTRAME", "DETALLE", "FOLIOS"]):
        detalle = detalle_operativo(pregunta)
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

# ==========================================
# INSIGHTS AUTOMÁTICOS
# ==========================================

def generar_insights():
    try:
        solicitudes = obtener_solicitudes()
        if not solicitudes:
            return "No hay suficientes datos para generar insights."
        
        metricas = obtener_metricas(solicitudes)
        total = metricas["total"]
        productivas = metricas["productivas"]
        efectividad = round((productivas / total) * 100, 1) if total > 0 else 0
        
        insights = []
        if efectividad > 80:
            insights.append("• El nivel de efectividad general es óptimo (>80%).")
        elif efectividad < 60:
            insights.append("• Alerta: La efectividad general se encuentra por debajo del estándar esperado.")
            
        criticas = total_criticas(solicitudes)
        if criticas > 0:
            insights.append(f"• Se detectaron {criticas} solicitudes con antigüedad mayor a 7 días que requieren atención urgente.")
        else:
            insights.append("• Excelente control de tiempos: no hay solicitudes críticas críticas pendientes.")
            
        return "\n".join(insights)
    except Exception as e:
        return f"Error generando insights: {e}"


# ==========================================
# ENRUTADOR DE COMANDOS / RESPONDER IA
# ==========================================

def responder_trade_ai(pregunta):
    if not pregunta:
        return "Por favor, escribe una pregunta o comando válido."
    
    p = pregunta.strip().upper()
    
    # Detección de folios específicos
    if p.startswith("FOLIO ") or "TRD-" in p:
        match = re.search(r'(TRD-\d+)', p)
        if match:
            return buscar_folio(match.group(1))
        
    if "RESUMEN" in p and "EJECUTIVO" in p:
        return resumen_ejecutivo()
    elif "RESUMEN" in p:
        return obtener_resumen_general()
    elif "ABIERTAS" in p:
        return solicitudes_abiertas()
    elif "PRODUCTIVAS" in p and "IM" not in p:
        return solicitudes_productivas()
    elif "IMPRODUCTIVAS" in p:
        return solicitudes_improductivas()
    elif "MODELO" in p or "INCIDENCIA" in p or "FALLAS" in p:
        return top_modelos()
    elif "JEFATURA" in p:
        return top_jefaturas()
    elif "CANAL" in p:
        return top_canales()
    elif "GEC" in p:
        return top_gec()
    elif "ASESOR" in p:
        return top_asesores()
    elif "RUTA" in p:
        return top_rutas()
    elif "USUARIO" in p:
        return top_usuarios()
    elif "EFECTIVIDAD" in p:
        return efectividad_jefaturas()
    elif "CRITICA" in p or "ATRASADA" in p or "7 DÍAS" in p or "DIAS" in p:
        return solicitudes_criticas()
    elif "TENDENCIA" in p or "AUMENTANDO" in p or "FRECUENTE" in p or "CRECIMIENTO" in p:
        return tendencias_solicitudes()
    elif "RANKING" in p:
        return ranking_operativo()
    elif "ALERTA" in p:
        return alertas_inteligentes()
    elif "CENTRO EJECUTIVO" in p:
        return centro_ejecutivo()
    elif "INSIGHT" in p:
        return generar_insights()
    elif "PRIORIDAD" in p or "REVISAR HOY" in p or "URGENTE" in p:
        return prioridades_del_dia()
    else:
        return f"""
No comprendí con exactitud tu solicitud: "{pregunta}"

Te sugiero consultar alguno de los siguientes comandos:
• RESUMEN GENERAL
• SOLICITUDES ABIERTAS
• TOP MODELOS
• TOP JEFATURAS
• CRITICAS
• ALERTAS
• O escribe directamente un folio como: FOLIO TRD-000001
"""
