import streamlit as st
import pandas as pd
from utils.styles import aplicar_estilos_globales
from database import get_connection
from utils.excel import exportar_excel
from utils.pdf import generar_pdf_solicitud  # <--- Importamos la función que creamos


def reportes() -> None:
    """Muestra la interfaz de reportes gerenciales con filtros, gráficos y descarga en PDF."""
    st.subheader("Reportes Gerenciales")

    conn = get_connection()
    try:
        df = pd.read_sql(
            """
            SELECT *
            FROM solicitudes
            ORDER BY id DESC
            """,
            conn
        )
    except Exception as e:
        st.error(f"Error al cargar los datos de reportes: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()

    if df.empty:
        st.warning("No existen registros")
        return

    # --- Filtros de canal y estatus ---
    if "canal" in df.columns:
        canales_disponibles = sorted(df["canal"].dropna().unique().tolist())
        canal = st.selectbox("Canal", ["TODOS"] + canales_disponibles)
        if canal != "TODOS":
            df = df[df["canal"] == canal]

    if "estatus" in df.columns:
        estatus_disponibles = sorted(df["estatus"].dropna().unique().tolist())
        estatus = st.selectbox("Estatus", ["TODOS"] + estatus_disponibles)
        if estatus != "TODOS":
            df = df[df["estatus"] == estatus]

    if df.empty:
        st.warning("No hay registros que coincidan con los filtros seleccionados.")
        return

    # Métricas y Gráficos
    total = len(df)
    productivas = len(df[df["resultado"] == "PRODUCTIVO"]) if "resultado" in df.columns else 0
    efectividad = round((productivas / total) * 100, 2) if total > 0 else 0

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Solicitudes", total)
    with c2:
        st.metric("Efectividad", f"{efectividad}%")

    st.divider()

    # Visualización de la tabla de detalles
    st.write("### Detalle de Solicitudes")
    st.dataframe(df, use_container_width=True)

    # ==========================================
    # SECCIÓN DE DESCARGAS (EXCEL Y PDF)
    # ==========================================
    st.divider()
    st.write("### Opciones de Exportación")

    col_excel, col_pdf = st.columns(2)

    with col_excel:
        excel = exportar_excel(df, "Reporte")
        st.download_button(
            label="📥 Descargar Reporte en Excel",
            data=excel,
            file_name="reporte_trade.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col_pdf:
        # Validamos si podemos ofrecer descarga individual de una solicitud con estatus PRODUCTIVA
        if "folio" in df.columns and not df.empty:
            
            # Condición actualizada para filtrar estrictamente estatus PRODUCTIVA
            condicion_pdf = (
                df["estatus"]
                .fillna("")
                .str.upper()
                .eq("PRODUCTIVA")
            )
            
            df_atendidas = df[condicion_pdf]

            if df_atendidas.empty:
                st.info("No existen solicitudes PRODUCTIVAS para generar comprobantes PDF.")
            else:
                folios_disponibles = df_atendidas["folio"].dropna().unique().tolist()
                
                folio_seleccionado = st.selectbox(
                    "Seleccionar Folio para Comprobante PDF",
                    folios_disponibles
                )

                if folio_seleccionado:
                    # Obtenemos los datos de la fila seleccionada
                    fila_solicitud = df_atendidas[df_atendidas["folio"] == folio_seleccionado].iloc[0].to_dict()
                    
                    # Consultamos y agregamos el detalle de requerimientos a la solicitud para el PDF
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
                            params=[folio_seleccionado]
                        )
                        fila_solicitud["detalle_requerimientos"] = detalle_req.to_dict("records")
                    except Exception as e:
                        st.error(f"Error al cargar los requerimientos para el PDF: {e}")
                        fila_solicitud["detalle_requerimientos"] = []
                    finally:
                        conn.close()
                    
                    pdf_bytes = generar_pdf_solicitud(fila_solicitud)
                    
                    st.download_button(
                        label=f"📄 Descargar PDF Folio: {folio_seleccionado}",
                        data=pdf_bytes,
                        file_name=f"solicitud_{folio_seleccionado}.pdf",
                        mime="application/pdf"
                    )
        else:
            st.info("No hay folios disponibles para generar comprobantes PDF.")