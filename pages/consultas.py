import os
import streamlit as st
import pandas as pd
from utils.styles import aplicar_estilos_globales
from database import get_connection
from utils.excel import exportar_excel

UPLOAD_FOLDER = "uploads"


def consultas() -> None:
    """Muestra la interfaz de consulta, filtrado, exportación y detalle de solicitudes."""
    st.subheader("Consulta de Solicitudes")

    conn = get_connection()
    try:
        df = pd.read_sql(
            """
            SELECT *
            FROM solicitudes
            ORDER BY id DESC
            """,
            conn,
        )
    except Exception as e:
        st.error(f"Error al cargar las solicitudes: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()

    if df.empty:
        st.warning("No existen registros")
        return

    buscar = st.text_input("Buscar Folio")

    if buscar:
        df = df[
            df["folio"]
            .str.contains(
                buscar,
                case=False,
                na=False
            )
        ]

    st.write(f"Registros encontrados: {len(df)}")
    st.dataframe(df, use_container_width=True)

    if df.empty:
        st.warning("No hay registros disponibles para exportar o detallar.")
        return

    excel = exportar_excel(df, "Consulta")
    st.download_button(
        label="📥 Exportar Excel",
        data=excel,
        file_name="consulta_trade.xlsx"
    )

    st.divider()

    folio = st.selectbox(
        "Seleccione Folio",
        df["folio"].tolist()
    )

    detalle = df[df["folio"] == folio]

    st.write("### Detalle")
    st.dataframe(detalle, use_container_width=True)

    # ==========================================
    # DETALLE DE REQUERIMIENTOS (Tarjetas / Containers)
    # ==========================================
    conn = get_connection()
    try:
        detalle_req = pd.read_sql(
            """
            SELECT *
            FROM solicitud_detalle
            WHERE folio = ?
            ORDER BY id
            """,
            conn,
            params=[folio]
        )
    except Exception as e:
        st.error(f"Error al cargar los requerimientos: {e}")
        detalle_req = pd.DataFrame()
    finally:
        conn.close()

    st.write("### 📋 Requerimientos")

    if detalle_req.empty:
        st.warning("No existen requerimientos asociados.")
    else:
        for _, req in detalle_req.iterrows():
            with st.container(border=True):
                st.markdown(
                    f"### {req['tipo_solicitud']}"
                )

                st.write(
                    f"**Categoría:** {req['categoria']}"
                )

                if req.get("modelo"):
                    st.write(
                        f"**Modelo:** {req['modelo']}"
                    )

                if req.get("cantidad"):
                    st.write(
                        f"**Cantidad:** {req['cantidad']}"
                    )

                if req.get("serie"):
                    st.write(
                        f"**Serie:** {req['serie']}"
                    )

                if req.get("comentarios"):
                    st.info(
                        req["comentarios"]
                    )

        # Resumen en tabla y métrica
        st.write("### 📋 Resumen de Requerimientos")
        st.dataframe(
            detalle_req,
            use_container_width=True
        )
        st.metric(
            "Total Requerimientos",
            len(detalle_req)
        )

    # ==========================================
    # EVIDENCIAS
    # ==========================================
    conn = get_connection()
    try:
        docs = pd.read_sql(
            """
            SELECT *
            FROM documentos
            WHERE folio = ?
            """,
            conn,
            params=(folio,)
        )
    except Exception as e:
        st.error(f"Error al cargar las evidencias: {e}")
        docs = pd.DataFrame()
    finally:
        conn.close()

    st.write("### Evidencias")

    if docs.empty:
        st.info("No existen evidencias")
    else:
        for _, doc in docs.iterrows():
            archivo = os.path.join(
                UPLOAD_FOLDER,
                doc["archivo"]
            )

            if os.path.exists(archivo):
                with open(archivo, "rb") as f:
                    st.download_button(
                        label=f"📎 {doc['archivo']}",
                        data=f.read(),
                        file_name=doc["archivo"],
                        key=f"descarga_{doc['id']}"
                    )