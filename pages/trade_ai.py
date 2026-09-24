import streamlit as st
from services.ai_service import (
    responder_trade_ai,
    obtener_metricas,
    ultimos_folios,
    generar_insights
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
¿Qué jefatura tiene más solicitudes?
Muéstrame los indicadores.
FOLIO TRD-XXXXXX
"""
    )

    # ==========================================
    # BOTONES RÁPIDOS
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
