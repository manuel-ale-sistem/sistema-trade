import uuid
from datetime import datetime


def generar_folio() -> str:
    """Genera un folio único con formato: TRD-AAAAMMDD-XXXXXX"""
    fecha_actual = datetime.now().strftime("%Y%m%d")
    sufijo_aleatorio = uuid.uuid4().hex[:6].upper()
    
    return f"TRD-{fecha_actual}-{sufijo_aleatorio}"