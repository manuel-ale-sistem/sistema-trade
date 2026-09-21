import os
import uuid

import streamlit as st
import pandas as pd

from supabase_config import supabase

CARPETA_IMAGENES = "catalogos_img"
CARPETA_PDF = "catalogos_pdf"

os.makedirs(
    CARPETA_IMAGENES,
    exist_ok=True
)

os.makedirs(
    CARPETA_PDF,
    exist_ok=True
)


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

            conn = get_connection()
            cur = conn.cursor()

            imagen_path = ""
            pdf_path = ""

            # Imagen
            if (
                tipo == "MODELO"
                and imagen_modelo is not None
            ):

                extension = (
                    imagen_modelo.name
                    .split(".")[-1]
                    .lower()
                )

                nombre_imagen = (
                    f"{uuid.uuid4().hex}.{extension}"
                )

                imagen_path = os.path.join(
                    CARPETA_IMAGENES,
                    nombre_imagen
                )

                with open(
                    imagen_path,
                    "wb"
                ) as f:

                    f.write(
                        imagen_modelo.getbuffer()
                    )

            # PDF
            if (
                tipo == "MODELO"
                and pdf_modelo is not None
            ):

                nombre_pdf = (
                    f"{uuid.uuid4().hex}.pdf"
                )

                pdf_path = os.path.join(
                    CARPETA_PDF,
                    nombre_pdf
                )

                with open(
                    pdf_path,
                    "wb"
                ) as f:

                    f.write(
                        pdf_modelo.getbuffer()
                    )

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
                "Catálogo guardado correctamente"
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

        conn = get_connection()

        if mostrar_eliminados:
            consulta = """
            SELECT *
            FROM catalogos
            ORDER BY tipo, valor
            """
        else:
            consulta = """
            SELECT *
            FROM catalogos
            WHERE eliminado=0
            ORDER BY tipo, valor
            """

        df = pd.read_sql(
            consulta,
            conn
        )

        conn.close()

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

                if (
                    pd.notna(
                        fila["pdf_path"]
                    )
                    and fila["pdf_path"]
                ):
                    st.success(
                        "📄 Ficha Técnica Disponible"
                    )

                    with open(
                        fila["pdf_path"],
                        "rb"
                    ) as pdf_file:

                        st.download_button(
                            "📥 Descargar PDF",
                            data=pdf_file.read(),
                            file_name=f"{fila['valor']}.pdf",
                            mime="application/pdf"
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
                    conn = get_connection()
                    cur = conn.cursor()

                    cur.execute(
                        """
                        UPDATE catalogos
                        SET activo=1
                        WHERE id=?
                        """,
                        (registro,)
                    )

                    conn.commit()
                    conn.close()

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
                    conn = get_connection()
                    cur = conn.cursor()

                    cur.execute(
                        """
                        UPDATE catalogos
                        SET activo=0
                        WHERE id=?
                        """,
                        (registro,)
                    )

                    conn.commit()
                    conn.close()

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
                    conn = get_connection()
                    cur = conn.cursor()

                    cur.execute(
                        """
                        UPDATE catalogos
                        SET eliminado=0
                        WHERE id=?
                        """,
                        (registro,)
                    )

                    conn.commit()
                    conn.close()

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
                        conn = get_connection()
                        cur = conn.cursor()

                        cur.execute(
                            """
                            UPDATE catalogos
                            SET eliminado=1
                            WHERE id=?
                            """,
                            (registro,)
                        )

                        conn.commit()
                        conn.close()

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

            conn = get_connection()

            total = pd.read_sql(
                """
                SELECT COUNT(*) total
                FROM catalogos
                """,
                conn
            )

            activos = pd.read_sql(
                """
                SELECT COUNT(*) total
                FROM catalogos
                WHERE activo=1
                AND eliminado=0
                """,
                conn
            )

            inactivos = pd.read_sql(
                """
                SELECT COUNT(*) total
                FROM catalogos
                WHERE activo=0
                AND eliminado=0
                """,
                conn
            )

            eliminados = pd.read_sql(
                """
                SELECT COUNT(*) total
                FROM catalogos
                WHERE eliminado=1
                """,
                conn
            )

            conn.close()

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Total",
                int(total["total"][0])
            )

            c2.metric(
                "Activos",
                int(activos["total"][0])
            )

            c3.metric(
                "Inactivos",
                int(inactivos["total"][0])
            )

            c4.metric(
                "Eliminados",
                int(eliminados["total"][0])
            )
