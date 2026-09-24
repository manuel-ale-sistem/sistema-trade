import streamlit as st

from services.ai_service import (
    responder_trade_ai
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
