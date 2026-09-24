import streamlit as st

from services.ai_service import (
    responder_trade_ai
)


def trade_ai():

    st.subheader(
        "🤖 Trade AI Assistant"
    )

    st.info(
        """
Comandos disponibles:

RESUMEN

ABIERTAS

PRODUCTIVAS

IMPRODUCTIVAS

TOP MODELOS

TOP JEFATURAS

TOP CANALES

TOP GEC

FOLIO TRD-XXXXXX
"""
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
