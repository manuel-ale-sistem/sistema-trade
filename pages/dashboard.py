import streamlit as st
import pandas as pd
from utils.styles import aplicar_estilos_globales
from database import get_connection


def dashboard() -> None:
    """Muestra el dashboard ejecutivo con métricas de desempeño y gráficos de solicitudes."""
    st.subheader("Dashboard Ejecutivo")

    conn = get_connection()
    try:
        df = pd.read_sql(
            """
            SELECT *
            FROM solicitudes
            """,
            conn
        )
    except Exception as e:
        st.error(f"Error al cargar los datos del dashboard: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()

    if df.empty:
        st.warning("No existen registros")
        return

    total = len(df)

    capturadas = len(
        df[df["estatus"] == "CAPTURADA"]
    ) if "estatus" in df.columns else 0

    productivas = len(
        df[df["resultado"] == "PRODUCTIVO"]
    ) if "resultado" in df.columns else 0

    improductivas = len(
        df[df["resultado"] == "IMPRODUCTIVO"]
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
    conn = get_connection()
    try:
        modelos = pd.read_sql(
            """
            SELECT
                modelo,
                SUM(cantidad) total
            FROM solicitud_detalle
            WHERE modelo IS NOT NULL
            AND modelo <> ''
            GROUP BY modelo
            ORDER BY total DESC
            """,
            conn
        )
    except Exception as e:
        st.error(f"Error al cargar los modelos solicitados: {e}")
        modelos = pd.DataFrame()
    finally:
        conn.close()

    if not modelos.empty:
        st.write("### 🧊 Modelos Más Solicitados")
        st.bar_chart(
            modelos.set_index("modelo")["total"]
        )

    # ==========================================
    # SOLICITUDES POR CATEGORÍA (Dashboard Categorías)
    # ==========================================
    conn = get_connection()
    try:
        categorias = pd.read_sql(
            """
            SELECT
                categoria,
                COUNT(*) total
            FROM solicitud_detalle
            GROUP BY categoria
            ORDER BY total DESC
            """,
            conn
        )
    except Exception as e:
        st.error(f"Error al cargar las solicitudes por categoría: {e}")
        categorias = pd.DataFrame()
    finally:
        conn.close()

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