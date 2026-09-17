from io import BytesIO
import pandas as pd


def exportar_excel(df: pd.DataFrame, hoja: str = "Datos") -> bytes:
    """Exporta un DataFrame de pandas a un archivo Excel en memoria (bytes).

    Args:
        df (pd.DataFrame): DataFrame a exportar.
        hoja (str): Nombre de la hoja de cálculo en el archivo Excel.

    Returns:
        bytes: Contenido del archivo Excel listo para descargas (ej. Streamlit).
    """
    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:
        df.to_excel(
            writer,
            sheet_name=hoja,
            index=False
        )

    return output.getvalue()