import streamlit as st
import pandas as pd
from utils.styles import aplicar_estilos_globales
from supabase_config import supabase


def dashboard() -> None:
    """Muestra el dashboard ejecutivo con métricas de desempeño y gráficos de solicitudes."""
    st.subheader("Dashboard Ejecutivo")

    # ==========================================
    # CARGAR SOLICITUDES DESDE SUPABASE
    # ==========================================
    try:
        response = (
            supabase
            .table("solicitudes")
            .select("*")
            .execute()
        )

        df = pd.DataFrame(response.data)

    except Exception as e:
        st.error(
            f"Error al cargar los datos del dashboard: {e}"
        )
        df = pd.DataFrame()

    if df.empty:
        st.warning("No existen registros")
        return

    total = len(df)

    capturadas = len(
        df[df["estatus"] == "CAPTURADA"]
    ) if "estatus" in df.columns else 0

    productivas = len(
        df[
            df["resultado"]
            .fillna("")
            .eq("PRODUCTIVO")
        ]
    ) if "resultado" in df.columns else 0

    improductivas = len(
        df[
            df["resultado"]
            .fillna("")
            .eq("IMPRODUCTIVO")
        ]
    ) if "resultado" in df.columns else 0

    efectividad = 0
    if total > 0:
        efectividad = round((productivas / total) * 100, 2)

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Total", total)
    c2.metric("Capturadas", capturadas)
    c3.metric("Productivas", productivas)
    c4.metric("Improductivas", improductivas)
    c5.metric("Efectividad", f"{efectividad}%")

    st.divider()

    # ==========================================
    # MODELOS MÁS SOLICITADOS
    # ==========================================
    try:
        response = (
            supabase
            .table("solicitud_detalle")
            .select(
                "modelo,cantidad"
            )
            .execute()
        )

        detalle = pd.DataFrame(
            response.data
        )

        if not detalle.empty:
            detalle = detalle[
                detalle["modelo"].notna()
            ]

            detalle = detalle[
                detalle["modelo"] != ""
            ]

            modelos = (
                detalle
                .groupby("modelo")["cantidad"]
                .sum()
                .reset_index(name="total")
                .sort_values(
                    "total",
                    ascending=False
                )
            )
        else:
            modelos = pd.DataFrame()

    except Exception as e:
        st.error(
            f"Error al cargar modelos: {e}"
        )
        modelos = pd.DataFrame()

    if not modelos.empty:
        st.write("### 🧊 Modelos Más Solicitados")
        st.bar_chart(
            modelos.set_index("modelo")["total"]
        )

    # ==========================================
    # SOLICITUDES POR CATEGORÍA
    # ==========================================
    try:
        response = (
            supabase
            .table("solicitud_detalle")
            .select("categoria")
            .execute()
        )

        detalle_cat = pd.DataFrame(
            response.data
        )

        if not detalle_cat.empty:
            categorias = (
                detalle_cat
                .groupby("categoria")
                .size()
                .reset_index(name="total")
                .sort_values(
                    "total",
                    ascending=False
                )
            )
        else:
            categorias = pd.DataFrame()

    except Exception as e:
        st.error(
            f"Error al cargar categorías: {e}"
        )
        categorias = pd.DataFrame()

    if not categorias.empty:
        st.write("### 📊 Solicitudes por Categoría")
        st.bar_chart(
            categorias.set_index("categoria")["total"]
        )

    st.divider()

    if "canal" in df.columns:
        st.write("### Solicitudes por Canal")
        st.bar_chart(df["canal"].value_counts())

    if "estatus" in df.columns:
        st.write("### Solicitudes por Estatus")
        st.bar_chart(df["estatus"].value_counts())

    if "jefatura" in df.columns:
        st.write("### Solicitudes por Jefatura")
        st.bar_chart(df["jefatura"].value_counts())

    st.write("### Últimas Solicitudes")
    st.dataframe(
        df.head(50),
        use_container_width=True
    )
