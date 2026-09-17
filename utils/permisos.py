from utils.roles import *


PERMISOS = {
    SUPERADMIN: [
        "CAPTURA",
        "CONSULTAS",
        "GESTION",
        "USUARIOS",
        "CATALOGOS",
        "HISTORIAL",
        "REPORTES",
        "DASHBOARD",
        "ACCESOS"
    ],
    ADMIN: [
        "CAPTURA",
        "CONSULTAS",
        "GESTION",
        "USUARIOS",
        "CATALOGOS",
        "HISTORIAL",
        "REPORTES",
        "DASHBOARD"
    ],
    SUPERVISOR: [
        "CAPTURA",
        "CONSULTAS",
        "GESTION",
        "REPORTES",
        "DASHBOARD"
    ],
    GESTOR: [
        "GESTION",
        "CONSULTAS"
    ],
    CONSULTA: [
        "CONSULTAS"
    ],
    USUARIO: [
        "CAPTURA",
        "CONSULTAS"
    ]
}


def tiene_permiso(rol: str, modulo: str) -> bool:
    """Verifica si un rol tiene permiso para acceder a un módulo específico."""
    permisos = PERMISOS.get(rol, [])
    return modulo in permisos