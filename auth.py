import bcrypt
import streamlit as st
from supabase_config import supabase
from services.accesos_service import registrar_acceso

# Consulta inicial de prueba (opcional)
response = (
    supabase.table("usuarios")
    .select("*")
    .execute()
)

st.write("TODOS LOS USUARIOS:", response.data)

def verificar_password(password, password_hash):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


def login(usuario, password):
    try:
        response = (
            supabase.table("usuarios")
            .select("*")
            .eq("usuario", usuario)
            .execute()
        )

        st.write("DEBUG RESPONSE:", response.data)

        datos = response.data

        if not datos:
            st.error("Usuario no encontrado")
            return None

        usuario_db = datos[0]

        st.write("DEBUG HASH:", usuario_db["password"])
        st.write("DEBUG ACTIVO:", usuario_db["activo"])

        resultado = verificar_password(
            password,
            usuario_db["password"]
        )

        st.write("DEBUG PASSWORD OK:", resultado)

        if resultado:
            registrar_acceso(usuario, "LOGIN")
            return usuario_db

        return None

    except Exception as e:
        st.error(f"ERROR LOGIN: {e}")
        return None
