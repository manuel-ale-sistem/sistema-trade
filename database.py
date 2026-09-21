import bcrypt
from supabase_config import supabase


def hash_password(password):
    """Genera un hash seguro para la contraseña usando bcrypt."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def create_tables():
    """Nota: En Supabase las tablas se crean directamente mediante el panel SQL Editor."""
    pass


def crear_admin():
    """Crea un usuario administrador por defecto en Supabase si no existe."""
    try:
        response = supabase.table("usuarios").select("id").eq("usuario", "admin").execute()
        
        if not response.data:
            password_hasheado = hash_password("admin123")
            supabase.table("usuarios").insert({
                "usuario": "admin",
                "password": password_hasheado,
                "nombre": "ADMINISTRADOR",
                "rol": "ADMIN",
                "activo": 1
            }).execute()
    except Exception as e:
        print(f"Error al verificar/crear admin en Supabase: {e}")


def crear_catalogos_base():
    """Inserta catálogos por defecto en Supabase si aún no están registrados."""
    catalogos_base = [
        ("CANAL", "Canal Moderno"),
        ("CANAL", "Centro de Consumo"),
        ("CANAL", "Punto de Venta"),
        ("CANAL", "Six"),
        ("GEC", "ORO"),
        ("GEC", "PLATA"),
        ("GEC", "PLATINO"),
        ("GEC", "TITANIUM")
    ]

    try:
        for tipo, valor in catalogos_base:
            res = supabase.table("catalogos").select("id").eq("tipo", tipo).eq("valor", valor).execute()
            if not res.data:
                supabase.table("catalogos").insert({
                    "tipo": tipo,
                    "valor": valor,
                    "activo": 1,
                    "eliminado": 0
                }).execute()
    except Exception as e:
        print(f"Error al inicializar catálogos en Supabase: {e}")
