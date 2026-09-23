import streamlit as st
import pandas as pd
from services.storage_service import subir_archivo
from supabase_config import supabase


def catalogos():

    st.subheader(
        "Administración de Catálogos"
    )

    tab1, tab2 = st.tabs(
        [
            "Nuevo Registro",
            "Administrar"
        ]
    )

    # =====================================
    # NUEVO
    # =====================================

    with tab1:

        tipo = st.selectbox(
            "Tipo",
            [
                "JEFATURA",
                "RUTA",
                "CANAL",
                "SOLICITUD",
                "GEC",
                "SEGMENTO",
                "MODELO"
            ]
        )

        valor = st.text_input(
            "Valor"
        )

        imagen_modelo = None
        pdf_modelo = None

        if tipo == "MODELO":

            imagen_modelo = st.file_uploader(
                "Imagen del Modelo",
                type=["jpg", "jpeg", "png"]
            )

            pdf_modelo = st.file_uploader(
                "Ficha Técnica PDF",
                type=["pdf"]
            )

        if st.button(
            "Guardar Catálogo"
        ):

            if not valor.strip():
                st.error(
                    "Ingrese un valor"
                )
                return

            imagen_path = ""
            pdf_path = ""

            # Imagen -> Supabase Storage (trade-files/modelos/imagenes)
            if (
                tipo == "MODELO"
                and imagen_modelo is not None
            ):
                resultado_img = subir_archivo(
                    imagen_modelo, "modelos/imagenes"
                )
                if resultado_img and "url" in resultado_img:
                    imagen_path = resultado_img["url"]

            # PDF -> Supabase Storage (trade-files/modelos/pdf)
            if (
                tipo == "MODELO"
                and pdf_modelo is not None
            ):
                resultado_pdf = subir_archivo(
                    pdf_modelo, "modelos/pdf"
                )
                if resultado_pdf and "url" in resultado_pdf:
                    pdf_path = resultado_pdf["url"]

            supabase.table(
                "catalogos"
            ).insert(
                {
                    "tipo": tipo,
                    "valor": valor.strip(),
                    "imagen_path": imagen_path,
                    "pdf_path": pdf_path,
                    "activo": 1,
                    "eliminado": 0
                }
            ).execute()

            st.success(
                "Catálogo guardado correctamente en Supabase Storage y Base de Datos"
            )

            st.cache_data.clear()
            st.rerun()

    # =====================================
    # ADMINISTRAR
    # =====================================

    with tab2:

        mostrar_eliminados = st.checkbox(
            "Mostrar eliminados"
        )

        if mostrar_eliminados:

            response = (
                supabase
                .table("catalogos")
                .select("*")
                .order("tipo")
                .execute()
            )

        else:

            response = (
                supabase
                .table("catalogos")
                .select("*")
                .eq("eliminado", 0)
                .order("tipo")
                .execute()
            )

        df = pd.DataFrame(response.data)

        if df.empty:
            st.warning(
                "No existen registros."
            )
            return

        st.dataframe(
            df,
            use_container_width=True
        )

        registro = st.selectbox(
            "Seleccionar Registro",
            df["id"].tolist()
        )

        detalle = df[
            df["id"] == registro
        ]

        if not detalle.empty:
            fila = detalle.iloc[0]

            if fila["tipo"] == "MODELO":

                # Mostrar Imagen desde URL de Supabase
                if (
                    pd.notna(
                        fila["imagen_path"]
                    )
                    and fila["imagen_path"]
                ):
                    try:
                        st.image(
                            fila["imagen_path"],
                            width=300
                        )
                    except Exception:
                        st.warning(
                            "No fue posible mostrar la imagen."
                        )

                # Botón para abrir PDF desde URL de Supabase Storage
                if (
                    pd.notna(
                        fila["pdf_path"]
                    )
                    and fila["pdf_path"]
                ):
                    st.success(
                        "📄 Ficha Técnica Disponible en la Nube"
                    )
                    st.link_button(
                        "📥 Ver / Descargar Ficha PDF",
                        fila["pdf_path"]
                    )

            st.info(
                f"Tipo: {fila['tipo']} | "
                f"Valor: {fila['valor']} | "
                f"Activo: {fila['activo']}"
            )

            col1, col2, col3, col4 = st.columns(4)

            # =====================================
            # ACTIVAR
            # =====================================

            with col1:
                if st.button(
                    "✅ Activar"
                ):
                    supabase.table(
                        "catalogos"
                    ).update(
                        {
                            "activo": 1
                        }
                    ).eq(
                        "id",
                        registro
                    ).execute()

                    st.success(
                        "Registro activado"
                    )
                    st.rerun()

            # =====================================
            # DESACTIVAR
            # =====================================

            with col2:
                if st.button(
                    "⛔ Desactivar"
                ):
                    supabase.table(
                        "catalogos"
                    ).update(
                        {
                            "activo": 0
                        }
                    ).eq(
                        "id",
                        registro
                    ).execute()

                    st.success(
                        "Registro desactivado"
                    )
                    st.rerun()

            # =====================================
            # ELIMINAR LOGICO
            # =====================================

            with col3:
                if st.button(
                    "🗑️ Eliminar"
                ):
                    st.session_state[
                        "confirmar_catalogo"
                    ] = registro

            # =====================================
            # RESTAURAR
            # =====================================

            with col4:
                if st.button(
                    "♻️ Restaurar"
                ):
                    supabase.table(
                        "catalogos"
                    ).update(
                        {
                            "eliminado": 0
                        }
                    ).eq(
                        "id",
                        registro
                    ).execute()

                    st.success(
                        "Registro restaurado"
                    )
                    st.rerun()

            # =====================================
            # CONFIRMAR ELIMINACION
            # =====================================

            if st.session_state.get(
                "confirmar_catalogo"
            ) == registro:

                st.warning(
                    "⚠️ ¿Desea eliminar este registro?"
                )

                c1, c2 = st.columns(2)

                with c1:
                    if st.button(
                        "CONFIRMAR"
                    ):
                        supabase.table(
                            "catalogos"
                        ).update(
                            {
                                "eliminado": 1
                            }
                        ).eq(
                            "id",
                            registro
                        ).execute()

                        st.session_state.pop(
                            "confirmar_catalogo",
                            None
                        )

                        st.success(
                            "Registro eliminado"
                        )
                        st.rerun()

                with c2:
                    if st.button(
                        "Cancelar"
                    ):
                        st.session_state.pop(
                            "confirmar_catalogo",
                            None
                        )
                        st.rerun()

            # =====================================
            # RESUMEN
            # =====================================

            st.divider()

            todos = (
                supabase.table("catalogos")
                .select("*")
                .execute()
            ).data

            total = len(todos)

            activos = len(
                [
                    x for x in todos
                    if x["activo"] == 1
                    and x["eliminado"] == 0
                ]
            )

            inactivos = len(
                [
                    x for x in todos
                    if x["activo"] == 0
                    and x["eliminado"] == 0
                ]
            )

            eliminados = len(
                [
                    x for x in todos
                    if x["eliminado"] == 1
                ]
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Total", total)
            c2.metric("Activos", activos)
            c3.metric("Inactivos", inactivos)
            c4.metric("Eliminados", eliminados)
