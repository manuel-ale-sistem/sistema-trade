import uuid
from supabase_config import supabase

BUCKET = "trade-files"


def subir_archivo(archivo, carpeta):

    extension = archivo.name.split(".")[-1]

    nombre = (
        f"{carpeta}/"
        f"{uuid.uuid4().hex}."
        f"{extension}"
    )

    supabase.storage.from_(BUCKET).upload(
        nombre,
        archivo.getvalue()
    )

    url = (
        supabase.storage
        .from_(BUCKET)
        .get_public_url(nombre)
    )

    return {
        "archivo": nombre,
        "url": url
    }
