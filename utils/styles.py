import streamlit as st

def aplicar_estilos_globales():
    """Aplica una paleta de colores y estilos CSS universales a todo el sistema Trade V4."""
    st.markdown(
        """
        <style>
            /* ==========================================
               ESTILOS GENERALES Y FONDO
               ========================================== */
            .stApp {
                background-color: #f8f9fa;
                color: #212529 !important; /* Color de texto general oscuro y legible */
            }

            /* Forzar color de texto en párrafos, etiquetas y textos generales */
            p, span, label, div, .stMarkdown {
                color: #212529;
            }

            /* Tipografía y color global para títulos y encabezados */
            h1, h2, h3, h4, h5, h6 {
                color: #1b365d !important;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            }

            /* ==========================================
               BOTONES PRINCIPALES Y SECUNDARIOS
               ========================================== */
            .stButton > button {
                background-color: #1b365d !important;
                color: white !important;
                border-radius: 6px !important;
                border: none !important;
                font-weight: bold !important;
                padding: 0.5rem 1rem !important;
                transition: background-color 0.2s ease-in-out;
            }

            .stButton > button:hover {
                background-color: #336699 !important;
                color: white !important;
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
               BARRA LATERAL (SIDEBAR)
               ========================================== */
            section[data-testid="stSidebar"] {
                background-color: #ffffff;
                border-right: 1px solid #e0e0e0;
            }

            section[data-testid="stSidebar"] p, 
            section[data-testid="stSidebar"] span, 
            section[data-testid="stSidebar"] label {
                color: #212529 !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
