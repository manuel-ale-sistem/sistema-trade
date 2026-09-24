import streamlit as st
import bcrypt
from utils.styles import aplicar_estilos_globales
from supabase_config import supabase
from auth import login
from services.cierre_service import cerrar_solicitudes_vencidas

# ==========================================
# CONFIGURACION
# ==========================================
st.set_page_config(
    page_title="Trade V4 Enterprise",
    page_icon="📋",
    layout="wide"
)

aplicar_estilos_globales()

# ==========================================
# FUNCIONES DE INICIALIZACIÓN (Supabase)
# ==========================================
def crear_admin():
    """Crea un usuario administrador por defecto en Supabase si no existe."""
    try:
        response = supabase.table("usuarios").select("id").eq("usuario", "admin").execute()
        if not response.data:
            password_hasheado = bcrypt.hashpw(
                "admin123".encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")
            
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


# ==========================================
# INICIALIZACION (Optimizada con caché)
# ==========================================
@st.cache_resource
def inicializar_sistema():
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

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Iniciar Sesión")
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Ingresar", use_container_width=True)

            if submitted:
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
    "Accesos",
    "Trade AI"
]

menu_usuario = [
    "Captura",
    "Consultas",
    "Trade AI"
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

elif menu == "Asistente IA":
    from pages.ia_asistente import ia_asistente
    ia_asistente()

# ==========================================
# PIE
# ==========================================
st.sidebar.markdown("---")
st.sidebar.caption("Trade V4 Enterprise | GRO-MOR")

# ==========================================
# LOGOUT
# ==========================================
if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.clear()
    st.rerun()
