import os
import shutil
from datetime import datetime

BACKUP_FOLDER = "backups"

# Crear la carpeta de respaldos si no existe al cargar el módulo
os.makedirs(BACKUP_FOLDER, exist_ok=True)


def generar_backup() -> str:
    """Crea una copia de seguridad de la base de datos principal (trade.db).

    Returns:
        str: La ruta del archivo de backup generado.
    
    Raises:
        FileNotFoundError: Si la base de datos principal aún no existe.
    """
    db_path = "trade.db"

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"No se encontró la base de datos en '{db_path}'.")

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    destino = os.path.join(
        BACKUP_FOLDER,
        f"trade_{fecha}.db"
    )

    shutil.copy(db_path, destino)

    return destino