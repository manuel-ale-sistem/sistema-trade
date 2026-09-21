import bcrypt
from supabase_config import supabase
from services.accesos_service import registrar_acceso


def verificar_password(password, password_hash):
    """Verifica si la contraseña coincide con el hash almacenado."""
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


def login(usuario, password):
    """Valida las credenciales del usuario en Supabase y registra el acceso."""
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

        if verificar_password(password, usuario_db["password"]):
            registrar_acceso(usuario, "LOGIN")
            return usuario_db

    except Exception as e:
        print(f"Error en login con Supabase: {e}")
        return None

    return None
            registrar_acceso(usuario, "LOGIN")
            return datos
    except Exception:
        return None

    return None
