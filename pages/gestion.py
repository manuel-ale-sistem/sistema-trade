
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.styles import aplicar_estilos_globales
from supabase_config import supabase
from services.historial_service import guardar_historial


def actualizar_estatus(
    folio: str,
    estatus: str
) -> None:
    """Actualiza rápidamente el estatus de una solicitud y registra el cambio en el historial."""
    try:
        (
            supabase
            .table("solicitudes")
            .update(
                {
                    "estatus": estatus
                }
            )
            .eq("folio", folio)
            .execute()
        )

        guardar_historial(
            folio,
            st.session_state.get(
                "usuario",
                "sistema"
            ),
            f"Cambio rápido a {estatus}"
        )

        st.success(
            f"Estatus actualizado a {estatus}"
        )

        st.rerun()

    except Exception as e:
        st.error(
            f"Error al actualizar el estatus: {e}"
        )


def gestionar() -> None:
    """Muestra la interfaz de gestión para dar seguimiento y cambiar estatus de solicitudes."""
    st.subheader("Gestión de Solicitudes")

    # ==========================================
    # CARGAR SOLICITUDES DESDE SUPABASE
    # ==========================================
    try:
        response = (
            supabase
            .table("solicitudes")
            .select("*")
            .order(
                "id",
                desc=True
            )
            .execute()
        )

        df = pd.DataFrame(
            response.data
        )

    except Exception as e:
        st.error(
            f"Error al cargar las solicitudes: {e}"
        )
        df = pd.DataFrame()

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

    if (
        filtro != "TODOS"
        and "estatus" in df.columns
    ):
        df = df[
            df["estatus"] == filtro
        ]

    st.dataframe(df, use_container_width=True)

    if df.empty:
        st.warning("No hay registros para el filtro seleccionado.")
        return

    if "folio" not in df.columns:
        st.error(
            "La columna folio no existe en solicitudes."
        )
        return

    folio = st.selectbox(
        "Solicitud",
        df["folio"].tolist()
    )

    solicitud = df[df["folio"] == folio]
    fila = solicitud.iloc[0]

    st.write("### Información")
    st.dataframe(solicitud, use_container_width=True)

    # ==========================================
    # CARGAR REQUERIMIENTOS DESDE SUPABASE
    # ==========================================
    try:
        response = (
            supabase
            .table("solicitud_detalle")
            .select("*")
            .eq(
                "folio",
                folio
            )
            .order("id")
            .execute()
        )

        detalle_req = pd.DataFrame(
            response.data
        )

    except Exception as e:
        st.error(
            f"Error al cargar los requerimientos: {e}"
        )
        detalle_req = pd.DataFrame()

    st.write("### 📋 Requerimientos")

    if not detalle_req.empty:
        st.dataframe(
            detalle_req,
            use_container_width=True
        )

        estatuses = [
            "CAPTURADA",
            "ASIGNADA",
            "EN_PROCESO",
            "VISITA_REALIZADA",
            "PRODUCTIVA",
            "IMPRODUCTIVA",
            "CANCELADA"
        ]

        indice = 0

        if (
            "estatus" in fila.index
            and fila["estatus"] in estatuses
        ):
            indice = estatuses.index(
                fila["estatus"]
            )

        nuevo_estatus = st.selectbox(
            "Nuevo Estatus",
            estatuses,
            index=indice
        )

        resultado = st.selectbox(
            "Resultado",
            [
                "",
                "PRODUCTIVO",
                "IMPRODUCTIVO"
            ]
        )

        # Validar existencia de columnas de gestión opcionales (usando comentarios_adr)
        val_responsable = str(fila["usuario_gestiona"]) if "usuario_gestiona" in df.columns and pd.notna(fila["usuario_gestiona"]) else ""
        val_comentarios = str(fila["comentarios_adr"]) if "comentarios_adr" in df.columns and pd.notna(fila["comentarios_adr"]) else ""

        responsable = st.text_input("Responsable", value=val_responsable)
        comentarios = st.text_area("Comentarios", value=val_comentarios)

        if st.button("Guardar Gestión"):
            try:
                fecha_cierre = ""

                if nuevo_estatus in [
                    "PRODUCTIVA",
                    "IMPRODUCTIVA",
                    "CANCELADA"
                ]:
                    fecha_cierre = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                (
                    supabase
                    .table("solicitudes")
                    .update(
                        {
                            "estatus": nuevo_estatus,
                            "resultado": resultado,
                            "comentarios_adr": comentarios,
                            "usuario_gestiona": responsable,
                            "fecha_cierre": fecha_cierre
                        }
                    )
                    .eq(
                        "folio",
                        folio
                    )
                    .execute()
                )

                guardar_historial(
                    folio,
                    st.session_state.get(
                        "usuario",
                        "sistema"
                    ),
                    f"Cambio de estatus a {nuevo_estatus}"
                )

                st.success(
                    "Gestión actualizada"
                )

                st.rerun()

            except Exception as e:
                st.error(
                    f"Error al guardar la gestión: {e}"
                )

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
