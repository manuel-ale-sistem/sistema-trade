import uuid
from supabase_config import supabase

BUCKET = "trade-files"


def subir_archivo(archivo, carpeta):
    extension = archivo.name.split(".")[-1].lower()
    
    nombre = (
        f"{carpeta}/"
        f"{uuid.uuid4().hex}."
        f"{extension}"
    )

    # Determinar el content-type correcto para evitar que se abra como texto
    content_type = "application/octet-stream" # por defecto
    if extension == "pdf":
        content_type = "application/pdf"
    elif extension in ["jpg", "jpeg"]:
        content_type = "image/jpeg"
    elif extension == "png":
        content_type = "image/png"

    # Subir a Supabase pasando las opciones con el content_type correcto
    supabase.storage.from_(BUCKET).upload(
        path=nombre,
        file=archivo.getvalue(),
        file_options={"content-type": content_type}
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
