import os
import streamlit as st
import pandas as pd
from utils.styles import aplicar_estilos_globales
from supabase_config import supabase
from utils.excel import exportar_excel

UPLOAD_FOLDER = "uploads"


def consultas() -> None:
    """Muestra la interfaz de consulta, filtrado, exportación y detalle de solicitudes."""
    st.subheader("Consulta de Solicitudes")

    # ==========================================
    # CARGAR SOLICITUDES DESDE SUPABASE
    # ==========================================
    try:
        response = (
            supabase
            .table("solicitudes")
            .select("*")
            .order("id", desc=True)
            .execute()
        )
        df = pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error al cargar las solicitudes: {e}")
        df = pd.DataFrame()

    if df.empty:
        st.warning("No existen registros")
        return

    buscar = st.text_input("Buscar Folio")

    if buscar:
        mascara = (
            df["folio"]
            .astype(str)
            .str.contains(
                buscar,
                case=False,
                na=False
            )
        )
        df = df[mascara]

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

    # ==========================================
    # SELECCIÓN DE FOLIO ROBUSTA
    # ==========================================
    if "folio" not in df.columns:
        st.error("La columna folio no existe.")
        return

    folio = st.selectbox(
        "Seleccione Folio",
        sorted(df["folio"].dropna().unique().tolist())
    )

    detalle = df[df["folio"] == folio]

    st.write("### Detalle")
    st.dataframe(detalle, use_container_width=True)

    # ==========================================
    # DETALLE DE REQUERIMIENTOS (SUPABASE)
    # ==========================================
    try:
        response_req = (
            supabase
            .table("solicitud_detalle")
            .select("*")
            .eq("folio", folio)
            .order(
                "fecha_registro",
                desc=False
            )
            .execute()
        )
        detalle_req = pd.DataFrame(response_req.data)
    except Exception as e:
        st.error(f"Error al cargar los requerimientos: {e}")
        detalle_req = pd.DataFrame()

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

                if pd.notna(req.get("modelo")) and req.get("modelo") != "":
                    st.write(
                        f"**Modelo:** {req['modelo']}"
                    )

                if pd.notna(req.get("cantidad")):
                    st.write(
                        f"**Cantidad:** {req['cantidad']}"
                    )

                if pd.notna(req.get("serie")) and req.get("serie") != "":
                    st.write(
                        f"**Serie:** {req['serie']}"
                    )

                if pd.notna(req.get("comentarios")) and req.get("comentarios") != "":
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
    # EVIDENCIAS (SUPABASE)
    # ==========================================
    try:
        response_docs = (
            supabase
            .table("documentos")
            .select("*")
            .eq("folio", folio)
            .execute()
        )
        docs = pd.DataFrame(response_docs.data)
    except Exception as e:
        st.error(f"Error al cargar las evidencias: {e}")
        docs = pd.DataFrame()

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
