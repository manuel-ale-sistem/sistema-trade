import streamlit as st
from utils.styles import aplicar_estilos_globales
from supabase_config import supabase
import os

st.write("URL:", os.getenv("SUPABASE_URL"))
st.write("KEY:", os.getenv("SUPABASE_KEY"))

try:
    resultado = supabase.table("usuarios").select("*").limit(1).execute()

    st.success("✅ Conexión con Supabase OK")
    st.write(resultado.data)

except Exception as e:
    st.error(f"❌ Error Supabase: {e}")
    
from database import (
    create_tables,
    crear_admin,
    crear_catalogos_base
)

from auth import login

from services.cierre_service import (
    cerrar_solicitudes_vencidas
)

# ==========================================
# CONFIGURACION
# ==========================================

st.set_page_config(
    page_title="Trade V4 Enterprise",
    page_icon="📋",
    layout="wide"
)

# ==========================================
# INICIALIZACION (Optimizada con caché)
# ==========================================

@st.cache_resource
def inicializar_sistema():
    create_tables()
    crear_admin()
    crear_catalogos_base()
    cerrar_solicitudes_vencidas()

inicializar_sistema()

# ==========================================
# LOGIN
# ==========================================

if "usuario" not in st.session_state:
    st.title("📋 Sistema Trade V4 Enterprise")
    st.markdown("---")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar", use_container_width=True):
        datos = login(usuario, password)

        if datos:
            st.session_state["usuario"] = datos["usuario"]
            st.session_state["nombre"] = datos["nombre"]
            st.session_state["rol"] = datos["rol"]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    st.stop()

# ==========================================
# ENCABEZADO
# ==========================================

st.title("📋 Trade V4 Enterprise")

st.sidebar.success(f"Usuario: {st.session_state['nombre']}")
st.sidebar.info(f"Rol: {st.session_state['rol']}")
st.sidebar.markdown("---")

# ==========================================
# MENUS
# ==========================================

menu_admin = [
    "Captura",
    "Dashboard",
    "Gestion",
    "Consultas",
    "Usuarios",
    "Catalogos",
    "Historial",
    "Reportes",
    "Accesos"
]

menu_usuario = [
    "Captura",
    "Consultas"
]

# ==========================================
# MENU SEGUN ROL
# ==========================================

if st.session_state["rol"] in ["ADMIN", "SUPERADMIN"]:
    menu = st.sidebar.radio("Menú", menu_admin)
else:
    menu = st.sidebar.radio("Menú", menu_usuario)

# ==========================================
# MODULOS
# ==========================================

if menu == "Captura":
    from pages.captura import captura_form
    captura_form()

elif menu == "Dashboard":
    from pages.dashboard import dashboard
    dashboard()

elif menu == "Gestion":
    from pages.gestion import gestionar
    gestionar()

elif menu == "Consultas":
    from pages.consultas import consultas
    consultas()

elif menu == "Usuarios":
    from pages.usuarios import usuarios
    usuarios()

elif menu == "Catalogos":
    from pages.catalogos import catalogos
    catalogos()

elif menu == "Historial":
    from pages.historial import historial
    historial()

elif menu == "Reportes":
    from pages.reportes import reportes
    reportes()

elif menu == "Accesos":
    from pages.accesos import accesos
    accesos()

# ==========================================
# PIE
# ==========================================

st.sidebar.markdown("---")
st.sidebar.caption("Trade V4 Enterprise | GRO-MOR")

# ==========================================
# BACKUP MANUAL
# ==========================================

try:
    from services.backup_service import generar_backup

    if st.sidebar.button("💾 Generar Backup", use_container_width=True):
        archivo = generar_backup()
        st.sidebar.success(f"Backup generado:\n{archivo}")
except Exception as e:
    # Opcional: st.sidebar.error(f"Error al cargar módulo de backup: {e}")
    pass

# ==========================================
# LOGOUT
# ==========================================

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.clear()
    st.rerun()
