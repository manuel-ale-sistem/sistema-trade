import re


def validar_sap(sap) -> bool:
    """Valida que el código SAP no esté vacío y tenga al menos 6 caracteres."""
    if not sap:
        return False
    
    # Convertir a string por si ingresan un número directamente
    sap_str = str(sap).strip()
    
    if len(sap_str) < 6:
        return False

    return True


def validar_telefono(telefono) -> bool:
    """Valida que el teléfono contenga exactamente 10 dígitos numéricos."""
    if not telefono:
        return False
        
    patron = r"^[0-9]{10}$"
    telefono_str = str(telefono).strip()
    
    return bool(re.match(patron, telefono_str))


def validar_texto(valor) -> bool:
    """Valida que el texto no esté vacío ni compuesto solo por espacios en blanco."""
    if not valor:
        return False

    if str(valor).strip() == "":
        return False

    return True