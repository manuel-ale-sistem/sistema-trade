import streamlit as st
from services.ai_service import (
    responder_trade_ai,
    obtener_metricas,
    ultimos_folios,
    generar_insights,
    centro_ejecutivo,
    alertas_inteligentes,
    predecir_efectividad_operativa
)


# ==========================================
# FUNCIÓN AUXILIAR PARA EL CHAT
# ==========================================
def agregar_a_chat(comando):
    """Auxiliar para evitar duplicar código en los botones rápidos."""
    if "chat_trade_ai" not in st.session_state:
        st.session_state["chat_trade_ai"] = []
    
    resultado = responder_trade_ai(comando)
    st.session_state.chat_trade_ai.append((comando, resultado))


def trade_ai():
    st.subheader("🤖 Trade AI Assistant")

    st.success(
        """
Bienvenido a Trade AI.
Puedes consultar información operativa,
folios, estadísticas e indicadores
del sistema Trade (¡Con Inteligencia Artificial Gemini integrada!).
"""
    )

    # ==========================================
    # KPIs
    # ==========================================
    metricas = obtener_metricas()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Solicitudes", metricas["total"])
    with col2:
        st.metric("📂 Abiertas", metricas["abiertas"])
    with col3:
        st.metric("✅ Productivas", metricas["productivas"])
    with col4:
        st.metric("❌ Improductivas", metricas["improductivas"])

    # ==========================================
    # EXPANDERS (RESUMEN, ALERTAS, INSIGHTS, ML)
    # ==========================================
    with st.expander("🤖 Resumen Ejecutivo IA", expanded=True):
        st.success(centro_ejecutivo())

    with st.expander("🚨 Alertas Inteligentes", expanded=True):
        st.warning(alertas_inteligentes())

    with st.expander("🤖 Insights Automáticos", expanded=True):
        st.info(generar_insights())

    with st.expander("🧠 Modelo Predictivo (Machine Learning)", expanded=False):
        if st.button("🚀 Ejecutar Entrenamiento y Predicción", use_container_width=True):
            with st.spinner("Entrenando modelo con Scikit-Learn..."):
                resultado_ml = predecir_efectividad_operativa()
                st.success(resultado_ml)
        else:
            st.info("Haz clic para entrenar el modelo predictivo de efectividad con base en datos históricos de Supabase.")

    # ==========================================
    # ULTIMOS FOLIOS
    # ==========================================
    st.markdown("### 📋 Últimos Folios")
    folios = ultimos_folios()
    for fila in folios:
        st.write(
            f"""
**{fila['folio']}**
Negocio: {fila['negocio']}
Estatus: {fila['estatus']}
"""
        )

    st.info(
        """
💬 Puedes usar comandos rápidos o invocar a Google Gemini escribiendo **IA** o **PREGUNTAR**:
• `IA ¿Por qué crees que la jefatura con más carga tiene tantas solicitudes?`
• `PREGUNTAR Redacta un correo ejecutivo para revisar las incidencias`
• Comandos rápidos: RESUMEN GENERAL | ABIERTAS | TOP MODELOS | CRITICAS | FOLIO TRD-XXXXXX
"""
    )

    # ==========================================
    # INICIALIZACIÓN DE ESTADO DEL CHAT
    # ==========================================
    if "chat_trade_ai" not in st.session_state:
        st.session_state["chat_trade_ai"] = []

    # ==========================================
    # BOTONES RÁPIDOS (FILA 1 Y 2)
    # ==========================================
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 RESUMEN", use_container_width=True):
            agregar_a_chat("RESUMEN")
    with col2:
        if st.button("🤖 INSIGHTS", use_container_width=True):
            agregar_a_chat("INSIGHTS")
    with col3:
        if st.button("📂 ABIERTAS", use_container_width=True):
            agregar_a_chat("ABIERTAS")

    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("🏆 ASESORES", use_container_width=True):
            agregar_a_chat("TOP ASESORES")
    with col5:
        if st.button("🛣 RUTAS", use_container_width=True):
            agregar_a_chat("TOP RUTAS")
    with col6:
        if st.button("📈 EFECTIVIDAD", use_container_width=True):
            agregar_a_chat("EFECTIVIDAD JEFATURAS")

    # ==========================================
    # ENTRADA DE CHAT (INPUT)
    # ==========================================
    pregunta = st.chat_input("Escribe una instrucción o 'IA [pregunta]'...")

    if pregunta:
        resultado = responder_trade_ai(pregunta)
        st.session_state["chat_trade_ai"].append((pregunta, resultado))

    # ==========================================
    # RENDERIZADO DEL HISTORIAL DEL CHAT
    # ==========================================
    for preg, resp in reversed(st.session_state["chat_trade_ai"]):
        with st.chat_message("user"):
            st.write(preg)

        with st.chat_message("assistant"):
            if isinstance(resp, dict) and "archivo" in resp:
                st.write(
                    f"""
📁 REPORTE EXCEL GENERADO
Archivo:
{resp["archivo"]}
Total de registros:
{resp["registros"]}
"""
                )
                try:
                    with open(resp["archivo"], "rb") as file:
                        st.download_button(
                            label="⬇️ Descargar Reporte",
                            data=file,
                            file_name=resp["archivo"],
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"Error al preparar el archivo para descarga: {e}")
            else:
                st.write(resp)
