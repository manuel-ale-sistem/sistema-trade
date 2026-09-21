import bcrypt
from supabase_config import supabase
from services.accesos_service import registrar_acceso


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
            .eq("activo", 1)
            .execute()
        )

        datos = response.data

        if not datos:
            return None

        usuario_db = datos[0]

        resultado = verificar_password(
            password,
            usuario_db["password"]
        )

        if resultado:
            registrar_acceso(
                usuario,
                "LOGIN"
            )
            return usuario_db

        return None

    except Exception as e:
        print(f"Error login: {e}")
        return None
