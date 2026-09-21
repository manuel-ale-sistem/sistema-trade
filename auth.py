import streamlit as st
import bcrypt
from supabase_config import supabase
from services.accesos_service import registrar_acceso


def login(usuario, password):

    try:

        response = (
            supabase.table("usuarios")
            .select("*")
            .eq("usuario", usuario)
            .eq("activo", 1)
            .execute()
        )

        st.write("DEBUG RESPONSE:", response.data)

        datos = response.data

        if not datos:
            st.error("DEBUG: Usuario no encontrado")
            return None

        usuario_db = datos[0]

        st.write("DEBUG USUARIO:", usuario_db["usuario"])
        st.write("DEBUG HASH:", usuario_db["password"])

        resultado = bcrypt.checkpw(
            password.encode("utf-8"),
            usuario_db["password"].encode("utf-8")
        )

        st.write("DEBUG PASSWORD OK:", resultado)

        if resultado:
            registrar_acceso(usuario, "LOGIN")
            return usuario_db

    except Exception as e:
        st.error(f"DEBUG ERROR: {e}")

    return None

            registrar_acceso(
                usuario,
                "LOGIN"
            )

            return usuario_db

        print("❌ Contraseña incorrecta")

    except Exception as e:
        print("ERROR LOGIN:", e)

    return None
