import streamlit as st

def aplicar_estilos_globales():
    """Aplica una paleta de colores y estilos CSS universales a todo el sistema Trade V4."""
    st.markdown(
        """
        <style>
            /* ==========================================
               ESTILOS GENERALES Y FONDO FORZADO
               ========================================== */
            .stApp, [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
                background-color: #f4f7fb !important;
                color: #212529 !important;
            }

            /* Forzar color de texto en elementos generales (EXCLUYENDO componentes flotantes de BaseWeb) */
            p, label, .stMarkdown {
                color: #212529;
            }
            
            /* Textos generales seguros que no rompan menús desplegables */
            span:not([data-baseweb]), div:not([data-baseweb]) {
                color: inherit;
            }

            /* Tipografía y color global para títulos y encabezados */
            h1, h2, h3, h4, h5, h6 {
                color: #1b365d !important;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            }

            /* ==========================================
               BOTONES MEJORADOS (st.button)
               ========================================== */
            .stButton > button {
                background-color: #1b365d !important;
                color: #ffffff !important;
                border-radius: 8px !important;
                border: 1px solid #1b365d !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
                padding: 0.55rem 1.2rem !important;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08) !important;
                transition: all 0.25s ease-in-out !important;
            }

            .stButton > button:hover {
                background-color: #2c4d7e !important;
                border-color: #2c4d7e !important;
                color: #ffffff !important;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
                transform: translateY(-1px);
            }

            .stButton > button:active {
                background-color: #132743 !important;
                transform: translateY(0px);
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
            }

            .stButton > button:focus {
                outline: none !important;
                box-shadow: 0 0 0 3px rgba(27, 54, 93, 0.3) !important;
            }

            /* ==========================================
               MÉTRICAS (st.metric)
               ========================================== */
            [data-testid="stMetricValue"] {
                color: #1b365d !important;
                font-weight: bold !important;
            }

            /* ==========================================
               PESTAÑAS (st.tabs)
               ========================================== */
            .stTabs [data-baseweb="tab-list"] {
                gap: 6px;
            }
            
            .stTabs [data-baseweb="tab"] {
                background-color: #ffffff;
                border-radius: 6px 6px 0px 0px;
                padding: 10px 20px;
                font-weight: bold;
                color: #555555;
                border: 1px solid #e0e0e0;
            }

            .stTabs [aria-selected="true"] {
                background-color: #1b365d !important;
                color: white !important;
                border-color: #1b365d !important;
            }

            /* ==========================================
               COMBOBOX Y SELECTORES (st.selectbox / multiselect)
               ========================================== */
            [data-baseweb="popover"] div, 
            [data-baseweb="menu"] div,
            [data-baseweb="select"] span {
                color: #212529 !important;
            }

            /* ==========================================
               BARRA LATERAL (SIDEBAR)
               ========================================== */
            section[data-testid="stSidebar"] {
                background-color: #ffffff;
                border-right: 1px solid #e0e0e0;
            }

            section[data-testid="stSidebar"] p, 
            section[data-testid="stSidebar"] span:not([data-baseweb]), 
            section[data-testid="stSidebar"] label {
                color: #212529 !important;
            }

            /* Ocultar el menú de páginas nativo y automático de Streamlit */
            [data-testid="stSidebarNav"] {
                display: none !important;
            }

            /* ==========================================
               MENÚ PERSONALIZADO (st.radio en el sidebar)
               ========================================== */
            section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
                background-color: transparent !important;
                border-radius: 6px !important;
                padding: 6px 10px !important;
                margin-bottom: 4px !important;
                transition: background-color 0.2s ease-in-out;
            }

            section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
                background-color: #f4f7fb !important;
            }

            section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label span {
                color: #212529 !important;
                font-weight: 500 !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
