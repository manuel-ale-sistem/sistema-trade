import streamlit as st
import os
from datetime import datetime
from database import get_connection

def captura_form():
    st.subheader("📋 Módulo de Captura de Solicitudes")
    st.markdown("---")

    # Obtener catálogos de la base de datos para los selects
    conn = get_connection()
    cur = conn.cursor()
    
    # Cargar Modelos con su respectiva ruta de imagen
    cur.execute("SELECT valor, imagen_path FROM catalogos WHERE tipo = 'MODELO' AND (eliminado = 0 OR eliminado IS NULL)")
    modelos_data = cur.fetchall()
    dict_modelos = {row["valor"]: row["imagen_path"] for row in modelos_data}
    lista_modelos = list(dict_modelos.keys()) if dict_modelos else ["Genérico"]

    # Cargar Canales
    cur.execute("SELECT valor FROM catalogos WHERE tipo = 'CANAL' AND (eliminado = 0 OR eliminado IS NULL)")
    canales_data = cur.fetchall()
    lista_canales = [row["valor"] for row in canales_data] if canales_data else ["Canal Moderno", "Punto de Venta"]

    # Cargar GEC
    cur.execute("SELECT valor FROM catalogos WHERE tipo = 'GEC' AND (eliminado = 0 OR eliminado IS NULL)")
    gecs_data = cur.fetchall()
    lista_gecs = [row["valor"] for row in gecs_data] if gecs_data else ["ORO", "PLATA"]
    
    conn.close()

    # ==========================================
    # SECCIÓN DE SELECCIÓN Y AYUDA VISUAL
    # ==========================================
    st.markdown("### 🔍 Selección de Modelo y Referencia Visual")
    col_sel, col_prev = st.columns([2, 1])

    with col_sel:
        modelo = st.selectbox("Modelo de Refrigerador", options=lista_modelos)

    with col_prev:
        ruta_imagen = dict_modelos.get(modelo, "")
        if ruta_imagen and os.path.exists(ruta_imagen):
            st.image(ruta_imagen, width=150, caption=f"Ref: {modelo}")
        else:
            st.info("📷 Sin imagen de referencia")

    st.markdown("---")

    # ==========================================
    # FORMULARIO COMPLETO DE CAPTURA
    # ==========================================
    with st.form("form_captura_completo"):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            folio = st.text_input("Folio")
            jefatura = st.text_input("Jefatura")
            ruta = st.text_input("Ruta")
            asesor = st.text_input("Asesor")
            
        with c2:
            canal = st.selectbox("Canal", lista_canales)
            solicitud = st.text_input("Solicitud")
            ppa = st.text_input("PPA")
            sap = st.text_input("SAP")
            
        with c3:
            negocio = st.text_input("Negocio")
            telefono = st.text_input("Teléfono")
            gec = st.selectbox("GEC", lista_gecs)
            segmento = st.text_input("Segmento")

        st.markdown("---")
        
        c4, c5 = st.columns(2)
        with c4:
            latitud = st.text_input("Latitud")
            longitud = st.text_input("Longitud")
        with c5:
            url_maps = st.text_input("URL Google Maps")

        observaciones = st.text_area("Observaciones")

        submitted = st.form_submit_button("💾 Guardar Solicitud", use_container_width=True)

        if submitted:
            if folio.strip() and negocio.strip():
                conn = get_connection()
                cur = conn.cursor()
                try:
                    cur.execute("""
                        INSERT INTO solicitudes (
                            folio, fecha, jefatura, ruta, asesor, canal, solicitud, 
                            ppa, sap, negocio, telefono, gec, modelo, segmento, 
                            latitud, longitud, url_maps, observaciones, estatus, usuario
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pendiente', ?)
                    """, (
                        folio.strip(), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        jefatura, ruta, asesor, canal, solicitud, ppa, sap,
                        negocio, telefono, gec, modelo, segmento, latitud, longitud,
                        url_maps, observaciones, st.session_state.get("usuario", "admin")
                    ))
                    conn.commit()

                    # Historial
                    cur.execute("""
                        INSERT INTO historial (folio, usuario, accion)
                        VALUES (?, ?, ?)
                    """, (folio.strip(), st.session_state.get("usuario", "admin"), "Creación de solicitud"))
                    conn.commit()

                    st.success(f"¡Solicitud {folio.strip()} registrada con éxito!")
                except Exception as e:
                    st.error(f"Error al guardar la solicitud (Folio posiblemente duplicado): {e}")
                finally:
                    conn.close()
            else:
                st.error("El Folio y el Negocio son obligatorios.")