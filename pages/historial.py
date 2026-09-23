import streamlit as st
import pandas as pd
from utils.styles import aplicar_estilos_globales
from supabase_config import supabase
from utils.excel import exportar_excel


def historial() -> None:
    """Muestra la interfaz de consulta del historial de movimientos con filtros y métricas desde Supabase."""
    st.subheader("Historial de Movimientos")

    try:
        # Consulta a la tabla historial en Supabase ordenada por id descendente
        response = (
            supabase.table("historial")
            .select("*")
            .order("id", desc=True)
            .execute()
        )
        df = pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error al cargar el historial desde Supabase: {e}")
        df = pd.DataFrame()

    if df.empty:
        st.warning("No existen movimientos")
        return

    col1, col2 = st.columns(2)

    with col1:
        filtro_usuario = st.text_input("Usuario")

    with col2:
        filtro_folio = st.text_input("Folio")

    if filtro_usuario and "usuario" in df.columns:
        df = df[
            df["usuario"]
            .astype(str)
            .str.contains(
                filtro_usuario,
                case=False,
                na=False
            )
        ]

    if filtro_folio and "folio" in df.columns:
        df = df[
            df["folio"]
            .astype(str)
            .str.contains(
                filtro_folio,
                case=False,
                na=False
            )
        ]

    c1, c2, c3 = st.columns(3)

    c1.metric("Movimientos", len(df))
    c2.metric("Usuarios", df["usuario"].nunique() if "usuario" in df.columns else 0)
    c3.metric("Folios", df["folio"].nunique() if "folio" in df.columns else 0)

    st.divider()

    st.dataframe(
        df,
        use_container_width=True
    )

    if df.empty:
        st.warning("No hay registros disponibles para exportar.")
        return

    excel = exportar_excel(df, "Historial")
    st.download_button(
        label="📥 Exportar Historial",
        data=excel,
        file_name="historial_trade.xlsx"
    )

    st.divider()

    if "folio" in df.columns:
        folios = (
            df["folio"]
            .dropna()
            .unique()
            .tolist()
        )

        if folios:
            folio = st.selectbox(
                "Seguimiento por Folio",
                folios
            )

            detalle = df[df["folio"] == folio]

            st.dataframe(
                detalle,
                use_container_width=True
            )

            st.info(f"Movimientos: {len(detalle)}")
