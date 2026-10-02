from collections import Counter
from datetime import datetime
import re
import pandas as pd
import plotly.express as px
import streamlit as st
from supabase_config import supabase


# ==========================================
# OBTENER DATOS (CAPA DE DATOS)
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
# HELPERS PRIVADOS (DRY - NO REPETIR CÓDIGO)
# ==========================================

def _obtener_contador_solicitudes(solicitudes, campo):
    contador = Counter()
    for fila in solicitudes:
        valor = fila.get(campo)
        if valor:
            contador[valor] += 1
    return contador


def _obtener_contador_detalles(campo="modelo"):
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
        return Counter(fila.get(campo) for fila in detalles if fila.get(campo))
    except Exception:
        return Counter()


def _formatear_top(titulo, contador, sufijo=""):
    if not contador:
        return f"{titulo}\n\nNo existen datos disponibles."
    respuesta = f"{titulo}\n\n"
    for nombre, cantidad in contador.most_common(10):
        respuesta += f"• {nombre}: {cantidad}{sufijo}\n"
    return respuesta


def _lider_generico(solicitudes, campo, titulo_label):
    if solicitudes is None:
        solicitudes = obtener_solicitudes()
    contador = _obtener_contador_solicitudes(solicitudes, campo)
    lider = contador.most_common(1)
    if not lider:
        return "No existen datos."
    return f"""
🏆 {titulo_label.upper()} LÍDER
{titulo_label.capitalize()}:
{lider[0][0]}
Solicitudes:
{lider[0][1]}
"""


def _parsear_dias(fecha, hoy=None):
    if not fecha:
        return None
    if hoy is None:
        hoy = datetime.now()
    try:
        fecha_sol = datetime.strptime(fecha[:10], "%Y-%m-%d")
        return (hoy - fecha_sol).days
    except Exception:
        return None


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
    return f"\n📂 SOLICITUDES ABIERTAS\n\nTotal:\n{metricas['abiertas']}\n"


def solicitudes_productivas():
    metricas = obtener_metricas()
    return f"\n✅ PRODUCTIVAS\n\nTotal:\n{metricas['productivas']}\n"


def solicitudes_improductivas():
    metricas = obtener_metricas()
    return f"\n❌ IMPRODUCTIVAS\n\nTotal:\n{metricas['improductivas']}\n"


# ==========================================
# TOP MODELOS / INCIDENCIAS
# ==========================================

def top_modelos():
    return _formatear_top("🏆 TOP MODELOS", _obtener_contador_detalles("modelo"))


def modelos_mayor_incidencia():
    return _formatear_top("🚨 MODELOS CON MÁS INCIDENCIAS", _obtener_contador_detalles("modelo"), sufijo=" incidencias")


# ==========================================
# TOPS GENERALES UNIFICADOS
# ==========================================

def top_jefaturas():
    return _formatear_top("🏆 TOP JEFATURAS", _obtener_contador_solicitudes(obtener_solicitudes(), "jefatura"))


def top_canales():
    return _formatear_top("🏆 TOP CANALES", _obtener_contador_solicitudes(obtener_solicitudes(), "canal"))


def top_gec():
    return _formatear_top("🏆 TOP GEC", _obtener_contador_solicitudes(obtener_solicitudes(), "gec"))


def top_asesores():
    return _formatear_top("🏆 TOP ASESORES", _obtener_contador_solicitudes(obtener_solicitudes(), "asesor"))


def top_rutas():
    return _formatear_top("🛣️ TOP RUTAS", _obtener_contador_solicitudes(obtener_solicitudes(), "ruta"))


def top_usuarios():
    contador = _obtener_contador_solicitudes(obtener_solicitudes(), "usuario")
    if not contador:
        return "\n👨‍💼 TOP USUARIOS\nNo existen datos disponibles.\n"
    return _formatear_top("👨‍💼 TOP USUARIOS CAPTURISTAS", contador, sufijo=" solicitudes")


# ==========================================
# EFECTIVIDAD
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
# SOLICITUDES CRÍTICAS
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
        dias = _parsear_dias(fila.get("fecha"), hoy)
        if dias is not None and dias >= 7:
            total += 1
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
        dias = _parsear_dias(fila.get("fecha"), hoy)
        if dias is not None and dias >= 7:
            encontradas += 1
            respuesta += f"• {fila.get('folio')} | {fila.get('negocio', 'N/D')} | {dias} días\n"
            
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
# TENDENCIAS
# ==========================================

def tendencias_solicitudes():
    try:
        contador = _obtener_contador_detalles("tipo_solicitud")
        if not contador:
            return "\n📈 TENDENCIAS\nNo existen datos suficientes.\n"
        return _formatear_top("📈 TENDENCIAS DE SOLICITUDES", contador, sufijo=" registros")
    except Exception as e:
        return f"Error analizando tendencias: {e}"


# ==========================================
# LÍDERES Y RANKING
# ==========================================

def jefatura_lider(solicitudes=None):
    return _lider_generico(solicitudes, "jefatura", "jefatura")


def asesor_lider(solicitudes=None):
    return _lider_generico(solicitudes, "asesor", "asesor")


def ruta_lider(solicitudes=None):
    return _lider_generico(solicitudes, "ruta", "ruta")


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
# UTILIDAD PRIVADA: ANÁLISIS DE JEFATURAS
# ==========================================

def _calcular_resumen_jefaturas(solicitudes):
    resumen = {}
    hoy = datetime.now()
    estatus_excluidos = {"PRODUCTIVA", "IMPRODUCTIVA", "CERRADA"}
    
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
            
        if estatus not in estatus_excluidos:
            resumen[jefatura]["abiertas"] += 1
            dias = _parsear_dias(fila.get("fecha"), hoy)
            if dias is not None and dias >= 7:
                resumen[jefatura]["criticas"] += 1
                
    return resumen


# ==========================================
# GRÁFICAS
# ==========================================

def grafica_jefaturas():
    solicitudes = obtener_solicitudes()
    contador = Counter(fila.get("jefatura") for fila in solicitudes if fila.get("jefatura"))
    df = pd.DataFrame(contador.items(), columns=["Jefatura", "Solicitudes"])
    return px.bar(df, x="Jefatura", y="Solicitudes", title="Solicitudes por Jefatura")


def grafica_canales():
    solicitudes = obtener_solicitudes()
    contador = Counter(fila.get("canal") for fila in solicitudes if fila.get("canal"))
    df = pd.DataFrame(contador.items(), columns=["Canal", "Solicitudes"])
    return px.pie(df, names="Canal", values="Solicitudes", title="Distribución por Canal")


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
    return px.bar(df, x="Modelo", y="Total", title="Top Modelos")


# ==========================================
# FUNCIONES UNIFICADAS Y ANALÍTICAS
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
            insights.append("• Excelente control de tiempos: no hay solicitudes críticas pendientes.")
            
        return "\n".join(insights)
    except Exception as e:
        return f"Error generando insights: {e}"


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


def diagnostico_ejecutivo():
    solicitudes = obtener_solicitudes()
    metricas = obtener_metricas(solicitudes)
    total = metricas["total"]
    productivas = metricas["productivas"]
    efectividad = round((productivas / total) * 100, 1) if total else 0
    criticas = total_criticas(solicitudes)
    lider = jefatura_lider(solicitudes)
    
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


def centro_ejecutivo():
    solicitudes = obtener_solicitudes()
    metricas = obtener_metricas(solicitudes)
    criticas = total_criticas(solicitudes)
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
            alertas.append(f"⚠️ La efectividad general es {efectividad}%.")
            
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


def prioridades_del_dia():
    solicitudes = obtener_solicitudes()
    if not solicitudes:
        return "\n📋 PRIORIDADES DEL DÍA\nNo existen datos suficientes.\n"

    prioridades = []
    criticas = []
    hoy = datetime.now()
    estatus_excluidos = {"PRODUCTIVA", "IMPRODUCTIVA", "CERRADA"}

    for fila in solicitudes:
        if fila.get("estatus") in estatus_excluidos:
            continue
        dias = _parsear_dias(fila.get("fecha"), hoy)
        if dias is not None and dias >= 7:
            criticas.append((fila.get("folio"), dias))

    if criticas:
        prioridades.append(f"🚨 Solicitudes críticas: {len(criticas)}")

    metricas = obtener_metricas(solicitudes)
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
            estatus_excluidos = {"PRODUCTIVA", "IMPRODUCTIVA", "CERRADA"}
            
            for s in solicitudes:
                val_campo = str(s.get(campo, "")).upper()
                estatus = s.get("estatus")
                is_prod = (estatus == "PRODUCTIVA")
                is_abierta = estatus not in estatus_excluidos
                
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
# RESPONDER IA (ENRUTADOR DE COMANDOS ÚNICO)
# ==========================================

def responder_trade_ai(pregunta):
    if not pregunta:
        return "Por favor, escribe una pregunta o comando válido."
        
    p = pregunta.strip().upper()
    
    # Búsqueda de folios
    if p.startswith("FOLIO ") or "TRD-" in p:
        match = re.search(r'(TRD-\d+)', p)
        if match:
            return buscar_folio(match.group(1))

    if "RESUMEN" in p and "EJECUTIVO" in p:
        return centro_ejecutivo()
    elif "RESUMEN" in p:
        return obtener_resumen_general()
    elif p == "ABIERTAS":
        return solicitudes_abiertas()
    elif p == "PRODUCTIVAS":
        return solicitudes_productivas()
    elif p == "IMPRODUCTIVAS":
        return solicitudes_improductivas()
    elif p == "TOP MODELOS" or p == "MODELOS":
        return top_modelos()
    elif any(x in p for x in ["INCIDENCIA", "INCIDENCIAS", "FALLAS"]):
        return modelos_mayor_incidencia()
    elif p == "TOP JEFATURAS" or p == "JEFATURAS":
        return top_jefaturas()
    elif p == "TOP CANALES" or p == "CANALES":
        return top_canales()
    elif p == "TOP GEC" or p == "GEC":
        return top_gec()
    elif p == "TOP ASESORES" or p == "ASESORES":
        return top_asesores()
    elif p == "TOP RUTAS" or p == "RUTAS":
        return top_rutas()
    elif p == "TOP USUARIOS" or p == "USUARIOS":
        return top_usuarios()
    elif "EFECTIVIDAD" in p:
        return efectividad_jefaturas()
    elif any(x in p for x in ["CRITICA", "CRÍTICA", "CRITICAS", "CRÍTICAS", "ATRASADA", "7 DÍAS"]):
        return solicitudes_criticas()
    elif any(x in p for x in ["TENDENCIA", "TENDENCIAS", "CRECIMIENTO"]):
        return tendencias_solicitudes()
    elif "RANKING" in p:
        return ranking_operativo()
    elif "ALERTA" in p:
        return alertas_inteligentes()
    elif "CENTRO EJECUTIVO" in p:
        return centro_ejecutivo()
    elif "INSIGHT" in p:
        return generar_insights()
    elif any(x in p for x in ["PRIORIDAD", "REVISAR HOY", "URGENTE"]):
        return prioridades_del_dia()
    elif "COMPARATIVO" in p or " VS " in p:
        return comparativo_inteligente(p)
    else:
        return f"""
No comprendí con exactitud tu solicitud: "{pregunta}"

Te sugiero consultar alguno de los siguientes comandos o escribir "AYUDA":
• RESUMEN GENERAL
• SOLICITUDES ABIERTAS
• TOP MODELOS
• TOP JEFATURAS
• CRITICAS
• ALERTAS
• CENTRO EJECUTIVO
• O escribe directamente un folio como: FOLIO TRD-000001
"""
