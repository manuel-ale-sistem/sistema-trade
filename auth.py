import bcrypt
import streamlit as st
from supabase_config import supabase
from services.accesos_service import registrar_acceso

def verificar_password(password, password_hash):
    """Verifica si la contraseña ingresada coincide con el hash almacenado."""
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


def login(usuario, password):
    """Realiza la autenticación del usuario consultando Supabase."""
    try:
        response = (
            supabase.table("usuarios")
            .select("*")
            .eq("usuario", usuario)
            .execute()
        )

        datos = response.data

        if not datos:
            st.error("Usuario no encontrado")
            return None

        usuario_db = datos[0]

        # Validar si el usuario está activo (opcional si manejas estatus)
        if usuario_db.get("activo", 1) == 0:
            st.error("Este usuario se encuentra inactivo")
            return None

        # Verificar la contraseña encriptada
        resultado = verificar_password(
            password,
            usuario_db["password"]
        )

        if resultado:
            registrar_acceso(usuario, "LOGIN")
            return usuario_db

        return None

    except Exception as e:
        st.error(f"Error en el sistema de autenticación: {e}")
        return None
