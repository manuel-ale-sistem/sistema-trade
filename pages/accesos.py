import streamlit as st
import pandas as pd
from utils.styles import aplicar_estilos_globales
from supabase_config import supabase


def accesos() -> None:
    """Muestra la bitácora de accesos del sistema en un componente interactivo de Streamlit desde Supabase."""
    st.subheader("Bitácora de Accesos")

    try:
        # Consulta a la tabla accesos en Supabase ordenada por id descendente
        response = (
            supabase.table("accesos")
            .select("*")
            .order("id", desc=True)
            .execute()
        )
        df = pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error al cargar la bitácora de accesos desde Supabase: {e}")
        df = pd.DataFrame()

    if df.empty:
        st.warning("No existen accesos registrados.")
        return

    st.write(f"Total accesos: {len(df)}")
    
    st.dataframe(
        df,
        use_container_width=True
    )
