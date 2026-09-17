import streamlit as st
import pandas as pd
from utils.styles import aplicar_estilos_globales
from database import (
    get_connection,
    hash_password
)


def crear_usuario(
    usuario,
    nombre,
    password,
    rol
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO usuarios(

            usuario,
            password,
            nombre,
            rol

        )

        VALUES(?,?,?,?)
        """,
        (
            usuario,
            hash_password(password),
            nombre,
            rol
        )
    )

    conn.commit()
    conn.close()


def activar_usuario(usuario):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        UPDATE usuarios

        SET activo=1

        WHERE usuario=?
        """,
        (usuario,)
    )

    conn.commit()
    conn.close()


def desactivar_usuario(usuario):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        UPDATE usuarios

        SET activo=0

        WHERE usuario=?
        """,
        (usuario,)
    )

    conn.commit()
    conn.close()


def reset_password(
    usuario,
    password
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        UPDATE usuarios

        SET password=?

        WHERE usuario=?
        """,
        (
            hash_password(password),
            usuario
        )
    )

    conn.commit()
    conn.close()


def usuarios():

    st.subheader(
        "Administración de Usuarios"
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "Crear",
            "Administrar",
            "Estadísticas"
        ]
    )

    # ==================================
    # CREAR
    # ==================================

    with tab1:

        usuario = st.text_input(
            "Usuario"
        )

        nombre = st.text_input(
            "Nombre Completo"
        )

        password = st.text_input(
            "Contraseña",
            type="password"
        )

        rol = st.selectbox(
            "Rol",
            [
                "ADMIN",
                "USUARIO"
            ]
        )

        if st.button(
            "Crear Usuario"
        ):

            try:

                crear_usuario(
                    usuario,
                    nombre,
                    password,
                    rol
                )

                st.success(
                    "Usuario creado"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    str(e)
                )

    # ==================================
    # ADMINISTRAR
    # ==================================

    with tab2:

        conn = get_connection()

        df = pd.read_sql(
            """
            SELECT

                id,
                usuario,
                nombre,
                rol,
                activo

            FROM usuarios

            ORDER BY id DESC
            """,
            conn
        )

        conn.close()

        st.dataframe(
            df,
            use_container_width=True
        )

        if df.empty:
            return

        usuario_sel = st.selectbox(
            "Usuario",
            df["usuario"].tolist()
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "Activar Usuario"
            ):

                activar_usuario(
                    usuario_sel
                )

                st.success(
                    "Usuario activado"
                )

                st.rerun()

        with c2:

            if st.button(
                "Desactivar Usuario"
            ):

                if usuario_sel.lower() == "admin":

                    st.error(
                        "No se puede desactivar admin"
                    )

                else:

                    desactivar_usuario(
                        usuario_sel
                    )

                    st.success(
                        "Usuario desactivado"
                    )

                    st.rerun()

        st.divider()

        nueva_password = st.text_input(
            "Nueva Contraseña",
            type="password"
        )

        if st.button(
            "Actualizar Contraseña"
        ):

            if nueva_password:

                reset_password(
                    usuario_sel,
                    nueva_password
                )

                st.success(
                    "Contraseña actualizada"
                )

                st.rerun()

    # ==================================
    # ESTADISTICAS
    # ==================================

    with tab3:

        conn = get_connection()

        total = pd.read_sql(
            """
            SELECT COUNT(*) total
            FROM usuarios
            """,
            conn
        )

        activos = pd.read_sql(
            """
            SELECT COUNT(*) total
            FROM usuarios
            WHERE activo=1
            """,
            conn
        )

        admins = pd.read_sql(
            """
            SELECT COUNT(*) total
            FROM usuarios
            WHERE rol='ADMIN'
            """,
            conn
        )

        conn.close()

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Usuarios",
            int(total["total"][0])
        )

        c2.metric(
            "Activos",
            int(activos["total"][0])
        )

        c3.metric(
            "Administradores",
            int(admins["total"][0])
        )
