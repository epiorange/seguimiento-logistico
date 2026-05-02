import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Sistema de Logística", page_icon="🚚")
st.title("🚚 Sistema de Logística")

# --------------------------------------------------
# DATOS DE SUPABASE
# --------------------------------------------------
SUPABASE_URL = "https://pdykvoknzspuaoupgzah.supabase.co"
SUPABASE_KEY = "sb_publishable_LVni99oPiIs9eExbU4fXvw_1l0mLpPj"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# --------------------------------------------------
# FUNCIONES
# --------------------------------------------------
def guardar_conductor(nombre, placa, telefono):
    url = f"{SUPABASE_URL}/rest/v1/conductores"
    data = {"nombre": nombre, "placa": placa, "telefono": telefono}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return True, "Conductor guardado correctamente"
    else:
        return False, f"Error {response.status_code}: {response.text}"
    
def guardar_cliente(nombre, empresa, email, telefono):
    """Registra un nuevo cliente en Supabase. Retorna (True, mensaje) o (False, error)."""
    url = f"{SUPABASE_URL}/rest/v1/clientes"
    data = {
        "nombre": nombre,
        "empresa": empresa if empresa else None,
        "email": email if email else None,
        "telefono": telefono if telefono else None
    }
    # Eliminar campos None para que Supabase los ignore (asignará NULL)
    data = {k: v for k, v in data.items() if v is not None}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return True, "Cliente registrado correctamente"
    except requests.exceptions.RequestException as e:
        # Intentar obtener el mensaje de error de Supabase
        try:
            error_detail = response.json()
            msg = error_detail.get('message', str(e))
        except:
            msg = str(e)
        return False, f"Error al guardar cliente: {msg}"

def obtener_conductores():
    url = f"{SUPABASE_URL}/rest/v1/conductores?select=*"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def obtener_clientes():
    """Obtiene la lista de clientes desde Supabase. Maneja errores de conexión y HTTP."""
    url = f"{SUPABASE_URL}/rest/v1/clientes?select=*"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener clientes: {e}")
        return []

def guardar_envio(conductor_id, origen, destino, cliente_id=None):
    """Crea un nuevo envío. El cliente es opcional."""
    url = f"{SUPABASE_URL}/rest/v1/envios"
    data = {
        "conductor_id": conductor_id,
        "origen": origen,
        "destino": destino,
        "estado": "pendiente"
    }
    if cliente_id is not None:
        data["cliente_id"] = cliente_id
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return True, "Envío creado correctamente"
    except requests.exceptions.RequestException as e:
        return False, f"Error al crear envío: {e}"
#AGREGUE NUEVA FUNCION PARA EL REGISTRO DE CLIENTES. 05022025
def pagina_registro_clientes():
    st.header("📋 Registro de Clientes")
    with st.form("form_cliente"):
        nombre = st.text_input("Nombre / Razón Social *")
        empresa = st.text_input("Empresa (opcional)")
        email = st.text_input("Correo electrónico")
        telefono = st.text_input("Teléfono")
        submitted = st.form_submit_button("Registrar Cliente")
        
        if submitted:
            if not nombre:
                st.warning("El nombre es obligatorio.")
            else:
                ok, msg = guardar_cliente(nombre, empresa, email, telefono)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
                        
# --------------------------------------------------
# INTERFAZ DE USUARIO CON BARRA LATERAL
# --------------------------------------------------
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a:", ["Registro de Conductores", "Crear Envío", "Registro de Clientes", "Panel del Conductor", "Rastrear Envío"])

if opcion == "Registro de Conductores":
    st.header("🚚 Registro de Conductores")
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
    st.markdown("---")
    st.subheader("📋 Conductores Registrados")
    conductores = obtener_conductores()
    if conductores:
        st.dataframe(conductores)
        st.metric("Total", len(conductores))
    else:
        st.info("Aún no hay conductores registrados")

elif opcion == "Crear Envío":
    st.header("📦 Crear Nuevo Envío")
    with st.form("form_envio"):
        conductores_lista = obtener_conductores()
        if conductores_lista:
            opciones = {f"{c['nombre']} (placa: {c['placa']})": c['id'] for c in conductores_lista}
            conductor_seleccionado = st.selectbox("Conductor", options=list(opciones.keys()))
            conductor_id = opciones[conductor_seleccionado]
        else:
            st.warning("Primero debes registrar al menos un conductor.")
            conductor_id = None
            
        # ---- NUEVO: Selector de Clientes ----
        clientes_lista = obtener_clientes()
        if clientes_lista:
            opciones_cliente = {f"{c['nombre']} ({c.get('empresa', 'Sin empresa')})": c['id'] for c in clientes_lista}
            cliente_seleccionado = st.selectbox("Cliente (opcional)", options=["Ninguno"] + list(opciones_cliente.keys()))
            if cliente_seleccionado != "Ninguno":
                cliente_id = opciones_cliente[cliente_seleccionado]
            else:
                cliente_id = None
        else:
            st.info("No hay clientes registrados. Puedes dejar el cliente sin asignar.")
            cliente_id = None

        origen = st.text_input("Origen")
        destino = st.text_input("Destino")

        submitted_envio = st.form_submit_button("Crear Envío")

        if submitted_envio and conductor_id:
            if origen and destino:
                ok, msg = guardar_envio(conductor_id, origen, destino, cliente_id)  # pasamos cliente_id
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Origen y destino son obligatorios")
        elif submitted_envio and not conductor_id:
            st.error("No hay conductores disponibles")    
##################################################
elif opcion == "Registro de Clientes":
    pagina_registro_clientes()            

########## ellif panel del condocutor#########

elif opcion == "Panel del Conductor":
    st.header("🚛 Panel del Conductor")
    conductores = obtener_conductores()
    if not conductores:
        st.warning("No hay conductores registrados.")
    else:
        nombres_conductores = [c["nombre"] for c in conductores]
        conductor_seleccionado_nombre = st.selectbox("Selecciona tu nombre", nombres_conductores)
        conductor_id = next(c["id"] for c in conductores if c["nombre"] == conductor_seleccionado_nombre)
        
        url_envios = f"{SUPABASE_URL}/rest/v1/envios?conductor_id=eq.{conductor_id}&select=*"
        response = requests.get(url_envios, headers=headers)
        if response.status_code == 200:
            envios = response.json()
            if not envios:
                st.info("No tienes envíos asignados.")
            else:
                opciones_envio = {f"ID {e['id']} - {e['origen']} → {e['destino']} (estado: {e['estado']})": e for e in envios}
                envio_seleccionado_str = st.selectbox("Selecciona un envío", list(opciones_envio.keys()))
                envio = opciones_envio[envio_seleccionado_str]
                
                st.subheader("📍 Actualizar ubicación")
                lat_inicial = envio.get("lat") or 4.5709
                lng_inicial = envio.get("lng") or -74.2973
                
                mapa = folium.Map(location=[lat_inicial, lng_inicial], zoom_start=12)
                if envio.get("lat") and envio.get("lng"):
                    folium.Marker([envio["lat"], envio["lng"]], popup="Última ubicación").add_to(mapa)
                output = st_folium(mapa, width=700, height=500)
                
                if output and output.get("last_clicked"):
                    lat = output["last_clicked"]["lat"]
                    lng = output["last_clicked"]["lng"]
                    url_update = f"{SUPABASE_URL}/rest/v1/envios?id=eq.{envio['id']}"
                    data_update = {"lat": lat, "lng": lng}
                    response_update = requests.patch(url_update, headers=headers, json=data_update)
                    if response_update.status_code in [200, 204]:
                        st.success(f"Ubicación actualizada: lat {lat:.4f}, lng {lng:.4f}")
                        st.rerun()
                    else:
                        st.error(f"Error al actualizar: {response_update.status_code}")
        else:
            st.error("Error al cargar los envíos")
#---------------------------------------------------
#RASTREO DE ENVIO
#----------------------------------------------------
elif opcion == "Rastrear Envío":
    st.header("🔍 Rastrear Envío")
    envio_id = st.number_input("ID del envío", min_value=1, step=1)
    if st.button("Buscar"):
        url = f"{SUPABASE_URL}/rest/v1/envios?id=eq.{envio_id}&select=*"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            datos = response.json()
            if datos:
                envio = datos[0]
                st.write(f"**Origen:** {envio['origen']}")
                st.write(f"**Destino:** {envio['destino']}")
                st.write(f"**Estado:** {envio['estado']}")
                if envio.get("lat") and envio.get("lng"):
                    st.subheader("Última ubicación conocida")
                    mapa = folium.Map(location=[envio["lat"], envio["lng"]], zoom_start=12)
                    folium.Marker([envio["lat"], envio["lng"]], popup="Ubicación del envío").add_to(mapa)
                    st_folium(mapa, width=700, height=500)
                else:
                    st.info("El conductor aún no ha reportado ubicación.")
            else:
                st.error("No se encontró un envío con ese ID.")
        else:
            st.error("Error al consultar el envío")
    