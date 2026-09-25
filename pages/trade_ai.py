import streamlit as st
from services.ai_service import (
    responder_trade_ai,
    obtener_metricas,
    ultimos_folios,
    generar_insights,
    resumen_ejecutivo,
    alertas_inteligentes
)


def trade_ai():

    st.subheader(
        "🤖 Trade AI Assistant"
    )

    st.success(
        """
Bienvenido a Trade AI.
Puedes consultar información operativa,
folios, estadísticas e indicadores
del sistema Trade.
"""
    )

    # ==========================================
    # KPIs
    # ==========================================
    metricas = obtener_metricas()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "📋 Solicitudes",
            metricas["total"]
        )
    with col2:
        st.metric(
            "📂 Abiertas",
            metricas["abiertas"]
        )
    with col3:
        st.metric(
            "✅ Productivas",
            metricas["productivas"]
        )
    with col4:
        st.metric(
            "❌ Improductivas",
            metricas["improductivas"]
        )

    # ==========================================
    # RESUMEN EJECUTIVO IA
    # ==========================================
    with st.expander(
        "🤖 Resumen Ejecutivo IA",
        expanded=True
    ):
        st.success(
            resumen_ejecutivo()
        )

    # ==========================================
    # ALERTAS INTELIGENTES
    # ==========================================
    with st.expander(
        "🚨 Alertas Inteligentes",
        expanded=True
    ):
        st.warning(
            alertas_inteligentes()
        )

    # ==========================================
    # INSIGHTS AUTOMATICOS
    # ==========================================
    with st.expander(
        "🤖 Insights Automáticos",
        expanded=True
    ):
        st.info(
            generar_insights()
        )

    # ==========================================
    # ULTIMOS FOLIOS
    # ==========================================
    st.markdown(
        "### 📋 Últimos Folios"
    )
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
💬 Puedes escribir preguntas naturales:
¿Cuántas solicitudes abiertas hay?
Dame un resumen general.
¿Cuál es el modelo más solicitado?
¿Qué modelo presenta más incidencias?
¿Qué modelos tienen más fallas?
Muéstrame incidencias.
¿Qué jefatura tiene más solicitudes?
Muéstrame los indicadores.
¿Hay solicitudes críticas?
Muéstrame las alertas operativas.
Muéstrame las alertas inteligentes.
¿Qué riesgos existen?
¿Hay anomalías operativas?
Monitoreo operativo.
¿Qué solicitudes llevan más de 7 días?
Solicitudes atrasadas.
¿Qué solicitudes están aumentando?
Muéstrame las tendencias.
¿Cuáles son las solicitudes más frecuentes?
¿Qué categoría tiene mayor crecimiento?
FOLIO TRD-XXXXXX
"""
    )

    # ==========================================
    # BOTONES RÁPIDOS (FILA 1)
    # ==========================================
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 RESUMEN", use_container_width=True):
            if "chat_trade_ai" not in st.session_state:
                st.session_state["chat_trade_ai"] = []
            st.session_state.chat_trade_ai.append(
                (
                    "RESUMEN",
                    responder_trade_ai("RESUMEN")
                )
            )

    with col2:
        if st.button("🤖 INSIGHTS", use_container_width=True):
            if "chat_trade_ai" not in st.session_state:
                st.session_state["chat_trade_ai"] = []
            st.session_state.chat_trade_ai.append(
                (
                    "INSIGHTS",
                    responder_trade_ai("INSIGHTS")
                )
            )

    with col3:
        if st.button("📂 ABIERTAS", use_container_width=True):
            if "chat_trade_ai" not in st.session_state:
                st.session_state["chat_trade_ai"] = []
            st.session_state.chat_trade_ai.append(
                (
                    "ABIERTAS",
                    responder_trade_ai("ABIERTAS")
                )
            )

    # ==========================================
    # BOTONES RÁPIDOS (FILA 2)
    # ==========================================
    col4, col5, col6 = st.columns(3)

    with col4:
        if st.button("🏆 ASESORES", use_container_width=True):
            if "chat_trade_ai" not in st.session_state:
                st.session_state["chat_trade_ai"] = []
            st.session_state.chat_trade_ai.append(
                (
                    "TOP ASESORES",
                    responder_trade_ai("TOP ASESORES")
                )
            )

    with col5:
        if st.button("🛣️ RUTAS", use_container_width=True):
            if "chat_trade_ai" not in st.session_state:
                st.session_state["chat_trade_ai"] = []
            st.session_state.chat_trade_ai.append(
                (
                    "TOP RUTAS",
                    responder_trade_ai("TOP RUTAS")
                )
            )

    with col6:
        if st.button("📈 EFECTIVIDAD", use_container_width=True):
            if "chat_trade_ai" not in st.session_state:
                st.session_state["chat_trade_ai"] = []
            st.session_state.chat_trade_ai.append(
                (
                    "EFECTIVIDAD JEFATURAS",
                    responder_trade_ai("EFECTIVIDAD JEFATURAS")
                )
            )

    if (
        "chat_trade_ai"
        not in st.session_state
    ):

        st.session_state[
            "chat_trade_ai"
        ] = []

    pregunta = st.chat_input(
        "Pregunta algo sobre Trade..."
    )

    if pregunta:

        respuesta = (
            responder_trade_ai(
                pregunta
            )
        )

        st.session_state[
            "chat_trade_ai"
        ].append(
            (
                pregunta,
                respuesta
            )
        )

    for pregunta, respuesta in reversed(
        st.session_state[
            "chat_trade_ai"
        ]
    ):

        with st.chat_message(
            "user"
        ):

            st.write(
                pregunta
            )

        with st.chat_message(
            "assistant"
        ):

            st.write(
                respuesta
            )
