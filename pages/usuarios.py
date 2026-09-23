import pandas as pd
import streamlit as st
from database import hash_password
from supabase_config import supabase
from utils.styles import aplicar_estilos_globales


def crear_usuario(usuario, nombre, password, rol):

  supabase.table("usuarios").insert({
      "usuario": usuario,
      "password": hash_password(password),
      "nombre": nombre,
      "rol": rol,
      "activo": 1,
  }).execute()


def activar_usuario(usuario):

  supabase.table("usuarios").update({"activo": 1}).eq("usuario", usuario).execute()


def desactivar_usuario(usuario):

  supabase.table("usuarios").update({"activo": 0}).eq("usuario", usuario).execute()


def reset_password(usuario, password):

  supabase.table("usuarios").update(
      {"password": hash_password(password)}
  ).eq("usuario", usuario).execute()


def usuarios():

  st.subheader("Administración de Usuarios")

  tab1, tab2, tab3 = st.tabs(["Crear", "Administrar", "Estadísticas"])

  # ==================================
  # CREAR
  # ==================================

  with tab1:

    usuario = st.text_input("Usuario")

    nombre = st.text_input("Nombre Completo")

    password = st.text_input("Contraseña", type="password")

    rol = st.selectbox("Rol", ["ADMIN", "USUARIO"])

    if st.button("Crear Usuario"):

      try:

        crear_usuario(usuario, nombre, password, rol)

        st.success("Usuario creado")

        st.rerun()

      except Exception as e:

        st.error(str(e))

  # ==================================
  # ADMINISTRAR
  # ==================================

  with tab2:

    response = (
        supabase.table("usuarios")
        .select("id,usuario,nombre,rol,activo")
        .order("id", desc=True)
        .execute()
    )

    df = pd.DataFrame(response.data)

    st.dataframe(df, use_container_width=True)

    if df.empty:
      return

    usuario_sel = st.selectbox("Usuario", df["usuario"].tolist())

    c1, c2 = st.columns(2)

    with c1:

      if st.button("Activar Usuario"):

        activar_usuario(usuario_sel)

        st.success("Usuario activado")

        st.rerun()

    with c2:

      if st.button("Desactivar Usuario"):

        if usuario_sel.lower() == "admin":

          st.error("No se puede desactivar admin")

        else:

          desactivar_usuario(usuario_sel)

          st.success("Usuario desactivado")

          st.rerun()

    st.divider()

    nueva_password = st.text_input("Nueva Contraseña", type="password")

    if st.button("Actualizar Contraseña"):

      if nueva_password:

        reset_password(usuario_sel, nueva_password)

        st.success("Contraseña actualizada")

        st.rerun()

  # ==================================
  # ESTADISTICAS
  # ==================================

  with tab3:

    response = supabase.table("usuarios").select("*").execute()

    usuarios_df = pd.DataFrame(response.data)

    if not usuarios_df.empty:
      total = len(usuarios_df)
      activos = len(usuarios_df[usuarios_df["activo"] == 1])
      admins = len(usuarios_df[usuarios_df["rol"] == "ADMIN"])
    else:
      total = 0
      activos = 0
      admins = 0

    c1, c2, c3 = st.columns(3)

    c1.metric("Usuarios", total)

    c2.metric("Activos", activos)

    c3.metric("Administradores", admins)
