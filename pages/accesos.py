import streamlit as st
import pandas as pd
from utils.styles import aplicar_estilos_globales
from database import get_connection


def accesos() -> None:
    """Muestra la bitácora de accesos del sistema en un componente interactivo de Streamlit."""
    st.subheader("Bitácora de Accesos")

    conn = get_connection()
    try:
        df = pd.read_sql(
            """
            SELECT *
            FROM accesos
            ORDER BY id DESC
            """,
            conn
        )
    except Exception as e:
        st.error(f"Error al cargar la bitácora de accesos: {e}")
        return
    finally:
        conn.close()

    if df.empty:
        st.warning("No existen accesos registrados.")
        return

    st.write(f"Total accesos: {len(df)}")
    
    st.dataframe(
        df,
        use_container_width=True
    )