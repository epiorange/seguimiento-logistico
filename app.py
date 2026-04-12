import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Registro de Conductores", page_icon="🚚")

# Título
st.title("🚚 Registro de Conductores")

# --------------------------------------------------
# DATOS DE SUPABASE (CÁMBIALOS POR LOS TUYOS)
# --------------------------------------------------
SUPABASE_URL = "https://pdykvoknzspuaoupgzah.supabase.co"  #   esta en subase en la parte de configuraciones
SUPABASE_KEY = "sb_publishable_LVni99oPiIs9eExbU4fXvw_1l0mLpPj"   #en configuraciones supbase

# Headers para la API de Supabase
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# --------------------------------------------------
# FUNCIONES
# --------------------------------------------------
def guardar_conductor(nombre, placa, telefono):
    """Envía los datos a Supabase usando POST"""
    url = f"{SUPABASE_URL}/rest/v1/conductores"
    data = {
        "nombre": nombre,
        "placa": placa,
        "telefono": telefono
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return True, "Conductor guardado correctamente"
    else:
        return False, f"Error {response.status_code}: {response.text}"

def obtener_conductores():
    """Obtiene la lista de conductores desde Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/conductores?select=*"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []
    
def guardar_envio(conductor_id, origen, destino):
    url = f"{SUPABASE_URL}/rest/v1/envios"
    data = {
        "conductor_id": conductor_id,
        "origen": origen,
        "destino": destino,
        "estado": "pendiente"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return True, "Envío creado correctamente"
    else:
        return False, f"Error: {response.status_code}"

# --------------------------------------------------
# FORMULARIO DE REGISTRO
# --------------------------------------------------
with st.form("form_registro"):
    st.subheader("📝 Nuevo Conductor")
    nombre = st.text_input("Nombre completo")
    placa = st.text_input("Placa del vehículo")
    telefono = st.text_input("Teléfono")
    submitted = st.form_submit_button("Registrar Conductor")
    
    if submitted:
        if nombre and placa and telefono:
            exito, mensaje = guardar_conductor(nombre, placa, telefono)
            if exito:
                st.success(mensaje)
                st.rerun()
            else:
                st.error(mensaje)
        else:
            st.warning("Completa todos los campos")

# --------------------------------------------------
# MOSTRAR LISTA DE CONDUCTORES
# --------------------------------------------------
st.markdown("---")
st.subheader("📋 Conductores Registrados")
conductores = obtener_conductores()

if conductores:
    st.dataframe(conductores)
    st.metric("Total", len(conductores))
else:
    st.info("Aún no hay conductores registrados")
    
# --------------------------------------------------
# NUEVO ENVÍO
# --------------------------------------------------
st.markdown("---")
st.subheader("📦 Crear nuevo envío")

with st.form("form_envio"):
    # Obtener conductores para el desplegable
    conductores_lista = obtener_conductores()
    if conductores_lista:
        # Crear un diccionario: nombre -> id
        opciones = {f"{c['nombre']} (placa: {c['placa']})": c['id'] for c in conductores_lista}
        conductor_seleccionado = st.selectbox("Conductor", options=list(opciones.keys()))
        conductor_id = opciones[conductor_seleccionado]
    else:
        st.warning("Primero debes registrar al menos un conductor.")
        conductor_id = None
    
    origen = st.text_input("Origen")
    destino = st.text_input("Destino")
    cliente_nombre = st.text_input("Nombre del cliente (opcional)")
    
    submitted_envio = st.form_submit_button("Crear Envío")
    
    if submitted_envio and conductor_id:
        if origen and destino:
            ok, msg = guardar_envio(conductor_id, origen, destino,)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
        else:
            st.warning("Origen y destino son obligatorios")
    elif submitted_envio and not conductor_id:
        st.error("No hay conductores disponibles para asignar el envío")
        
        