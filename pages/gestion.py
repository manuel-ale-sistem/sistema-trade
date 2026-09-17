import streamlit as st
import pandas as pd
from datetime import datetime
from utils.styles import aplicar_estilos_globales
from database import get_connection
from services.historial_service import guardar_historial


def actualizar_estatus(folio: str, estatus: str) -> None:
    """Actualiza rápidamente el estatus de una solicitud y registra el cambio en el historial."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE solicitudes
            SET estatus = ?
            WHERE folio = ?
            """,
            (estatus, folio)
        )
        conn.commit()

        guardar_historial(
            folio,
            st.session_state.get("usuario", "sistema"),
            f"Cambio rápido a {estatus}"
        )

        st.success(f"Estatus actualizado a {estatus}")
        st.rerun()
    except Exception as e:
        conn.rollback()
        st.error(f"Error al actualizar el estatus: {e}")
    finally:
        conn.close()


def gestionar() -> None:
    """Muestra la interfaz de gestión para dar seguimiento y cambiar estatus de solicitudes."""
    st.subheader("Gestión de Solicitudes")

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
        st.error(f"Error al cargar las solicitudes: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()

    if df.empty:
        st.warning("No existen solicitudes")
        return

    filtro = st.selectbox(
        "Filtrar Estatus",
        [
            "TODOS",
            "CAPTURADA",
            "ASIGNADA",
            "EN_PROCESO",
            "VISITA_REALIZADA",
            "PRODUCTIVA",
            "IMPRODUCTIVA",
            "CANCELADA"
        ]
    )

    if filtro != "TODOS":
        df = df[df["estatus"] == filtro]

    st.dataframe(df, use_container_width=True)

    if df.empty:
        st.warning("No hay registros para el filtro seleccionado.")
        return

    folio = st.selectbox(
        "Solicitud",
        df["folio"].tolist()
    )

    solicitud = df[df["folio"] == folio]
    fila = solicitud.iloc[0]

    st.write("### Información")
    st.dataframe(solicitud, use_container_width=True)

    # Cargar detalle de requerimientos
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

    if not detalle_req.empty:
        st.dataframe(
            detalle_req,
            use_container_width=True
        )

        nuevo_estatus = st.selectbox(
            "Nuevo Estatus",
            [
                "CAPTURADA",
                "ASIGNADA",
                "EN_PROCESO",
                "VISITA_REALIZADA",
                "PRODUCTIVA",
                "IMPRODUCTIVA",
                "CANCELADA"
            ]
        )

        resultado = st.selectbox(
            "Resultado",
            [
                "",
                "PRODUCTIVO",
                "IMPRODUCTIVO"
            ]
        )

        # Validar existencia de columnas de gestión opcionales
        val_responsable = str(fila["usuario_gestiona"]) if "usuario_gestiona" in df.columns and pd.notna(fila["usuario_gestiona"]) else ""
        val_comentarios = str(fila["comentarios_admin"]) if "comentarios_admin" in df.columns and pd.notna(fila["comentarios_admin"]) else ""

        responsable = st.text_input("Responsable", value=val_responsable)
        comentarios = st.text_area("Comentarios", value=val_comentarios)

        if st.button("Guardar Gestión"):
            fecha_cierre = ""
            if nuevo_estatus in ["PRODUCTIVA", "IMPRODUCTIVA", "CANCELADA"]:
                fecha_cierre = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE solicitudes
                    SET
                        estatus = ?,
                        resultado = ?,
                        comentarios_admin = ?,
                        usuario_gestiona = ?,
                        fecha_cierre = ?
                    WHERE folio = ?
                    """,
                    (
                        nuevo_estatus,
                        resultado,
                        comentarios,
                        responsable,
                        fecha_cierre,
                        folio
                    )
                )
                conn.commit()

                guardar_historial(
                    folio,
                    st.session_state.get("usuario", "sistema"),
                    f"Cambio de estatus a {nuevo_estatus}"
                )

                st.success("Gestión actualizada")
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Error al guardar la gestión: {e}")
            finally:
                conn.close()

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Asignar"):
            actualizar_estatus(folio, "ASIGNADA")

    with c2:
        if st.button("En Proceso"):
            actualizar_estatus(folio, "EN_PROCESO")

    with c3:
        if st.button("Visita Realizada"):
            actualizar_estatus(folio, "VISITA_REALIZADA")