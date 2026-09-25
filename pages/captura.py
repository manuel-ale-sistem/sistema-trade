import os
import uuid
import base64
import re
from zoneinfo import ZoneInfo
import streamlit as st
import pandas as pd
from supabase_config import supabase
from pathlib import Path
from datetime import datetime
from pypdf import PdfReader

from utils.folios import (
    generar_folio
)

from utils.validators import (
    validar_sap,
    validar_telefono,
    validar_texto
)

from services.historial_service import (
    guardar_historial
)

from services.storage_service import (
    subir_archivo
)

SOLICITUDES = {
    "SERV": [
        "Asignar Enfriador",
        "Asignar Barril",
        "Asignación Mobiliario",
        "Cambio Enfriador",
        "Cambio Barril",
        "Cambio Mobiliario",
        "Instalacion de Mobiliario",
        "Prestamo Mobiliario",
        "Reparación Enfriador",
        "Retiro Enfriador",
        "Retiro Barril",
        "Retiro Fachada",
        "Retiro Mobiliario",
        "Cambio de Equipo"
    ],
    "INIC": [
        "Boton o Anuncio Centro Consumo",
        "Estructura Punto Venta",
        "Incremento Capacidad Fria",
        "Mantenimiento Fachada",
        "Movimiento PPA con proveedor",
        "Retornabilidad",
        "Visibilidad Centro Consumo",
        "Render Fachada"
    ],
    "AVAS": [
        "Salidas AVAS"
    ],
    "RETI": [
        "REFR COOL DAY"
    ]
}

SOLICITUDES_CON_MODELO = [
    "Asignar Enfriador",
    "Cambio Enfriador",
    "Cambio de Equipo",
    "Retiro Enfriador"
]


@st.cache_data
def obtener_catalogo(tipo):
    response = (
        supabase
        .table("catalogos")
        .select("valor")
        .eq("tipo", tipo)
        .eq("activo", 1)
        .eq("eliminado", 0)
        .order("valor")
        .execute()
    )

    return [
        row["valor"]
        for row in response.data
    ]


@st.cache_data
def obtener_modelos():
    response = (
        supabase
        .table("catalogos")
        .select(
            "id,valor,imagen_path,pdf_path"
        )
        .eq("tipo", "MODELO")
        .eq("activo", 1)
        .eq("eliminado", 0)
        .order("valor")
        .execute()
    )

    return pd.DataFrame(
        response.data
    )


# ==========================================
# OBTENER Y GUARDAR ESPECIFICACIONES (SUPABASE)
# ==========================================

def obtener_especificaciones(
    catalogo_id
):
    response = (
        supabase
        .table("modelos_detalle")
        .select("*")
        .eq(
            "catalogo_id",
            catalogo_id
        )
        .execute()
    )

    return pd.DataFrame(
        response.data
    )


def guardar_especificaciones(
    catalogo_id,
    datos
):
    registro = {
        "catalogo_id": catalogo_id,
        **datos
    }

    supabase.table(
        "modelos_detalle"
    ).insert(
        registro
    ).execute()


# ==========================================
# GUARDAR DETALLE DE SOLICITUD (SUPABASE)
# ==========================================

def guardar_detalle_solicitud(
    folio,
    categoria,
    tipo_solicitud,
    modelo="",
    cantidad=1,
    serie="",
    comentarios="",
    reporte="",
    material="",
    capacidad_actual="",
    capacidad_solicitada=""
):
    supabase.table(
        "solicitud_detalle"
    ).insert(
        {
            "folio": folio,
            "categoria": categoria,
            "tipo_solicitud": tipo_solicitud,
            "modelo": modelo,
            "cantidad": cantidad,
            "serie": serie,
            "comentarios": comentarios,
            "reporte": reporte,
            "material": material,
            "capacidad_actual": capacidad_actual,
            "capacidad_solicitada": capacidad_solicitada
        }
    ).execute()


# ==========================================
# LEER PDF
# ==========================================

def leer_pdf(ruta_pdf):
    try:
        reader = PdfReader(
            ruta_pdf
        )

        texto = ""

        for pagina in reader.pages:
            contenido = pagina.extract_text()

            if contenido:
                texto += contenido + "\n"

        return texto

    except Exception:
        return ""


# ==========================================
# EXTRAER DATOS DEL PDF
# ==========================================

def extraer_datos_pdf(texto):
    datos = {}

    patrones = {
        "capacidad":
            r"(?i)capacidad.*?([0-9]+.*)",
        "voltaje":
            r"(?i)voltaje.*?([0-9]+.*)",
        "puertas":
            r"(?i)puertas.*?([0-9]+.*)",
        "refrigerante":
            r"(?i)(R[0-9]+|refrigerante.*)",
        "consumo":
            r"(?i)consumo.*?([0-9]+.*)",
        "temperatura":
            r"(?i)temperatura.*?([0-9]+.*)"
    }

    for campo, patron in patrones.items():
        resultado = re.search(
            patron,
            texto
        )

        if resultado:
            datos[campo] = (
                resultado
                .group(1)
                .strip()
            )

    return datos


def captura_form():
    if "requerimientos" not in st.session_state:
        st.session_state.requerimientos = []

    st.subheader(
        "Nueva Solicitud Trade"
    )

    if "ultimo_folio_registrado" in st.session_state and st.session_state.ultimo_folio_registrado:
        st.success(f"🎉 Última solicitud registrada exitosamente con el folio: **{st.session_state.ultimo_folio_registrado}**")

    # Obtener la hora actual ajustada a México
    fecha = datetime.now(ZoneInfo("America/Mexico_City")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    st.info(
        f"Fecha: {fecha}"
    )

    jefaturas = obtener_catalogo(
        "JEFATURA"
    )

    rutas = obtener_catalogo(
        "RUTA"
    )

    canales = obtener_catalogo(
        "CANAL"
    )

    gecs = obtener_catalogo(
        "GEC"
    )

    segmentos = obtener_catalogo(
        "SEGMENTO"
    )

    df_modelos = obtener_modelos()

    if df_modelos.empty:
        modelos = ["SIN DATOS"]
    else:
        modelos = (
            df_modelos["valor"]
            .tolist()
        )

    if not jefaturas:
        jefaturas = ["SIN DATOS"]

    if not rutas:
        rutas = ["SIN DATOS"]

    if not canales:
        canales = ["SIN DATOS"]

    if not gecs:
        gecs = ["SIN DATOS"]

    if not segmentos:
        segmentos = ["SIN DATOS"]

    col1, col2 = st.columns(2)

    with col1:
        jefatura = st.selectbox(
            "Jefatura",
            jefaturas
        )

        ruta = st.selectbox(
            "Ruta",
            rutas
        )

        asesor = st.text_input(
            "Asesor"
        )

        canal = st.selectbox(
            "Canal",
            canales
        )

        ppa = st.selectbox(
            "¿Nace en PPA?",
            [
                "N/A",
                "SI",
                "NO"
            ]
        )

    with col2:
        sap = st.text_input(
            "SAP Cliente"
        )

        negocio = st.text_input(
            "Negocio"
        )

        telefono = st.text_input(
            "Teléfono"
        )

        gec = st.selectbox(
            "GEC",
            gecs
        )

        segmento = st.selectbox(
            "Segmento",
            segmentos
        )

    # ==========================
    # REQUERIMIENTOS DINÁMICOS
    # ==========================

    st.markdown("## 📋 Requerimientos")

    categoria_req = st.selectbox(
        "Categoría",
        list(SOLICITUDES.keys())
    )

    tipo_req = st.selectbox(
        "Tipo de Solicitud",
        SOLICITUDES[categoria_req]
    )

    datos_requerimiento = {}

    # MODELO Y FICHA TÉCNICA
    if tipo_req in SOLICITUDES_CON_MODELO:
        datos_requerimiento["modelo"] = st.selectbox(
            "Modelo",
            modelos,
            key="req_modelo"
        )

        modelo_seleccionado = datos_requerimiento["modelo"]

        modelo_info = df_modelos[
            df_modelos["valor"] == modelo_seleccionado
        ]

        if not modelo_info.empty:
            ruta_imagen = (
                modelo_info.iloc[0]["imagen_path"]
            )

            ruta_pdf = (
                modelo_info.iloc[0]["pdf_path"]
            )

            if ruta_imagen:
                try:
                    st.markdown(
                        "### 🧊 Modelo Seleccionado"
                    )
                    st.image(
                        ruta_imagen,
                        width=300
                    )
                except Exception:
                    st.warning(
                        "Imagen no disponible"
                    )

            # Nota: Se eliminó completamente el bloque de st.metric de la Ficha Técnica para que no aparezca con N/D.
            # Si solo deseas descargarlo o ver el botón del PDF, se mantiene abajo:

            if ruta_pdf:
                st.link_button(
                    "📄 Descargar Ficha Técnica",
                    ruta_pdf
                )

    # CANTIDAD
    if tipo_req in [
        "Asignar Enfriador",
        "Asignar Barril",
        "Asignación Mobiliario",
        "Salidas AVAS"
    ]:
        datos_requerimiento["cantidad"] = st.number_input(
            "Cantidad",
            min_value=1,
            value=1,
            key="req_cantidad"
        )

    # SERIE
    if tipo_req in [
        "Cambio Enfriador",
        "Cambio Barril",
        "Cambio Mobiliario"
    ]:
        datos_requerimiento["serie"] = st.text_input(
            "Número de Serie"
        )

    # REPORTE
    if tipo_req == "Reparación Enfriador":
        datos_requerimiento["reporte"] = st.text_input(
            "Número de Reporte"
        )

    # CAPACIDADES
    if tipo_req == "Incremento Capacidad Fria":
        datos_requerimiento["capacidad_actual"] = st.text_input(
            "Capacidad Actual"
        )
        datos_requerimiento["capacidad_solicitada"] = st.text_input(
            "Capacidad Solicitada"
        )

    # MATERIAL
    if tipo_req == "Salidas AVAS":
        datos_requerimiento["material"] = st.text_input(
            "Material"
        )

    # COMENTARIOS
    datos_requerimiento["comentarios"] = st.text_area(
        "Comentarios"
    )

    if st.button("➕ Agregar Requerimiento"):
        if (
            tipo_req in SOLICITUDES_CON_MODELO
            and not datos_requerimiento.get("modelo")
        ):
            st.error(
                "Debe seleccionar un modelo"
            )
            st.stop()

        st.session_state.requerimientos.append({
            "categoria": categoria_req,
            "tipo": tipo_req,
            **datos_requerimiento
        })

        st.success(
            "Requerimiento agregado"
        )

        st.rerun()

    if st.session_state.requerimientos:
        st.markdown(
            "### ✅ Requerimientos Capturados"
        )

        for idx, req in enumerate(
            st.session_state.requerimientos
        ):
            with st.container(border=True):
                st.markdown(
                    f"### {idx+1}. {req['categoria']} - {req['tipo']}"
                )

                for key, value in req.items():
                    if key not in [
                        "categoria",
                        "tipo"
                    ]:
                        st.write(
                            f"**{key}:** {value}"
                        )

                if st.button(
                    "🗑 Eliminar",
                    key=f"del_{idx}"
                ):
                    st.session_state.requerimientos.pop(
                        idx
                    )

                    st.rerun()

    st.markdown(
        "### 📍 Ubicación"
    )

    url_maps = st.text_input(
        "Link Google Maps"
    )

    latitud = ""
    longitud = ""

    try:
        if "?q=" in url_maps:
            coordenadas = (
                url_maps
                .split("?q=")[1]
            )

            latitud, longitud = (
                coordenadas.split(",")
            )
    except Exception:
        latitud = ""
        longitud = ""

    observaciones = st.text_area(
        "Observaciones generales"
    )

    documentos = st.file_uploader(
        "Evidencias",
        type=[
            "pdf",
            "jpg",
            "jpeg",
            "png"
        ],
        accept_multiple_files=True
    )

    if st.button(
        "Guardar Solicitud",
        use_container_width=True
    ):
        if not validar_sap(sap):
            st.error(
                "SAP inválido"
            )
            return

        if not validar_texto(
            negocio
        ):
            st.error(
                "Ingrese negocio"
            )
            return

        if not validar_telefono(
            telefono
        ):
            st.error(
                "Teléfono inválido. Debe tener 10 dígitos."
            )
            return

        try:
            folio = generar_folio()

            supabase.table("solicitudes").insert(
                {
                    "folio": folio,
                    "fecha": fecha,
                    "jefatura": jefatura,
                    "ruta": ruta,
                    "asesor": asesor,
                    "canal": canal,
                    "solicitud": "MULTIPLE",
                    "ppa": ppa,
                    "sap": sap,
                    "negocio": negocio,
                    "telefono": telefono,
                    "gec": gec,
                    "modelo": "",
                    "segmento": segmento,
                    "latitud": latitud,
                    "longitud": longitud,
                    "url_maps": url_maps,
                    "observaciones": observaciones,
                    "estatus": "CAPTURADA",
                    "usuario": st.session_state["usuario"]
                }
            ).execute()

            for req in st.session_state.requerimientos:
                guardar_detalle_solicitud(
                    folio=folio,
                    categoria=req.get("categoria", ""),
                    tipo_solicitud=req.get("tipo", ""),
                    modelo=req.get("modelo", ""),
                    cantidad=req.get("cantidad", 1),
                    serie=req.get("serie", ""),
                    comentarios=req.get("comentarios", ""),
                    reporte=req.get("reporte", ""),
                    material=req.get("material", ""),
                    capacidad_actual=req.get("capacidad_actual", ""),
                    capacidad_solicitada=req.get("capacidad_solicitada", "")
                )

            if documentos:
                for archivo in documentos:
                    resultado = subir_archivo(
                        archivo,
                        "evidencias"
                    )

                    nombre_archivo = resultado[
                        "archivo"
                    ]

                    url = resultado[
                        "url"
                    ]

                    supabase.table("documentos").insert(
                        {
                            "folio": folio,
                            "archivo": nombre_archivo,
                            "url": url
                        }
                    ).execute()

            guardar_historial(
                folio,
                st.session_state["usuario"],
                "CREACION SOLICITUD"
            )

            st.session_state.requerimientos = []
            st.session_state.ultimo_folio_registrado = folio

            st.balloons()
            st.rerun()

        except Exception as e:
            st.error(
                f"Error: {e}"
            )
