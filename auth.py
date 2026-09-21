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

        print("RESPONSE:", response.data)

        datos = response.data

        if not datos:
            print("❌ Usuario no encontrado")
            return None

        usuario_db = datos[0]

        print("✅ Usuario encontrado:", usuario_db["usuario"])
        print("✅ Hash:", usuario_db["password"])

        resultado = verificar_password(
            password,
            usuario_db["password"]
        )

        print("✅ Resultado bcrypt:", resultado)

        if resultado:

            registrar_acceso(
                usuario,
                "LOGIN"
            )

            return usuario_db

        print("❌ Contraseña incorrecta")

    except Exception as e:
        print("ERROR LOGIN:", e)

    return None
