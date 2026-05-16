# ============================================
# IMPORTACIÓN DE LIBRERÍAS -------->>> primer sprint 
# ============================================
import streamlit as st          # Para construir la interfaz web
import requests                 # Para comunicarnos con Supabase (API REST)
import folium                   # Para crear mapas interactivos
from streamlit_folium import st_folium  # Para incrustar mapas de Folium en Streamlit
import pandas as pd             # Para manejo de datos (tablas)

# ============================================
# CONFIGURACIÓN DE LA PÁGINA ---------------->>>> primer sprint 
# ============================================
st.set_page_config(page_title="Sistema de Logística", page_icon="🚚")
st.title("🚚 Sistema de Logística")

# ============================================
# DATOS DE CONEXIÓN A SUPABASE ------>>> primer sprint 
# ============================================
# (Reemplaza con tus propias credenciales si es necesario)
SUPABASE_URL = "https://pdykvoknzspuaoupgzah.supabase.co"
SUPABASE_KEY = "sb_publishable_LVni99oPiIs9eExbU4fXvw_1l0mLpPj"

# Headers estándar para las peticiones a la API REST de Supabase
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ============================================
# INICIALIZACIÓN DEL ESTADO DE SESIÓN
# ============================================
# Estas variables se mantienen mientras el usuario interactúa con la app
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False  # Indica si hay un usuario logueado
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "rol" not in st.session_state:
    st.session_state.rol = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_nombre" not in st.session_state:
    st.session_state.user_nombre = None

# ============================================
# FUNCIONES DE ACCESO A DATOS (CONDUCTORES, CLIENTES, ENVÍOS)
# ============================================

def guardar_conductor(nombre, placa, telefono):
    """Envía un nuevo conductor a la tabla 'conductores' de Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/conductores"
    data = {"nombre": nombre, "placa": placa, "telefono": telefono}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return True, "Conductor guardado correctamente"
    else:
        return False, f"Error {response.status_code}: {response.text}"

def obtener_conductores():
    """Obtiene la lista completa de conductores desde Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/conductores?select=*"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def guardar_cliente(nombre, empresa, email, telefono):
    """Registra un nuevo cliente en la tabla 'clientes'."""
    url = f"{SUPABASE_URL}/rest/v1/clientes"
    data = {
        "nombre": nombre,
        "empresa": empresa if empresa else None,
        "email": email if email else None,
        "telefono": telefono if telefono else None
    }
    # Eliminamos campos con valor None para que Supabase los asigne como NULL
    data = {k: v for k, v in data.items() if v is not None}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return True, "Cliente registrado correctamente"
    except requests.exceptions.RequestException as e:
        # Intentamos extraer el mensaje de error de Supabase
        try:
            error_detail = response.json()
            msg = error_detail.get('message', str(e))
        except:
            msg = str(e)
        return False, f"Error al guardar cliente: {msg}"

def obtener_clientes():
    """Devuelve la lista de todos los clientes desde Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/clientes?select=*"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener clientes: {e}")
        return []

def guardar_envio(conductor_id, origen, destino, cliente_id=None):
    """Crea un nuevo envío asociado a un conductor y opcionalmente a un cliente."""
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

# ============================================
# FUNCIONES DE AUTENTICACIÓN (Supabase Auth)
# ============================================

def registrar_usuario(email, password, rol, nombre, telefono=None, empresa=None):
    """
    Registra un nuevo usuario en auth.users y crea su perfil en la tabla 'perfiles'.
    Retorna (éxito, mensaje, user_id).
    """
    # 1. Llamada a signup de Supabase Auth
    url_signup = f"{SUPABASE_URL}/auth/v1/signup"
    data_signup = {"email": email, "password": password}
    try:
        response = requests.post(url_signup, json=data_signup)
        response.raise_for_status()
        user_data = response.json()
        user_id = user_data.get("user", {}).get("id")
        if not user_id:
            return False, "No se pudo obtener el ID del usuario", None

        # 2. Insertar perfil en la tabla 'perfiles'
        url_perfil = f"{SUPABASE_URL}/rest/v1/perfiles"
        perfil_data = {
            "id": user_id,
            "email": email,
            "rol": rol,
            "nombre": nombre,
            "telefono": telefono,
            "empresa": empresa
        }
        # Usamos los mismos headers (con anon key). Como RLS está desactivado, funciona.
        response_perfil = requests.post(url_perfil, headers=headers, json=perfil_data)
        if response_perfil.status_code not in [200, 201]:
            return False, f"Error al crear perfil: {response_perfil.text}", user_id
        return True, "Usuario registrado correctamente", user_id
    except requests.exceptions.RequestException as e:
        return False, f"Error en registro: {e}", None

def iniciar_sesion(email, password):
    """
    Inicia sesión con email y contraseña.
    Retorna (éxito, mensaje, access_token, user_id, rol, nombre).
    """
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    data = {"email": email, "password": password}
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        session_data = response.json()
        access_token = session_data.get("access_token")
        user_id = session_data.get("user", {}).get("id")

        # Obtener rol y nombre desde la tabla 'perfiles'
        url_perfil = f"{SUPABASE_URL}/rest/v1/perfiles?id=eq.{user_id}&select=rol,nombre,empresa"
        resp_perfil = requests.get(url_perfil, headers=headers)
        if resp_perfil.status_code == 200 and resp_perfil.json():
            perfil = resp_perfil.json()[0]
            rol = perfil.get("rol")
            nombre = perfil.get("nombre")
        else:
            rol = None
            nombre = None
        return True, "Inicio de sesión exitoso", access_token, user_id, rol, nombre
    except requests.exceptions.RequestException as e:
        return False, f"Error al iniciar sesión: {e}", None, None, None, None

def cerrar_sesion():
    """Elimina todas las variables de sesión y recarga la aplicación."""
    for key in ["authenticated", "access_token", "user_id", "rol", "user_email", "user_nombre"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ============================================
# FUNCIONES DE LAS PÁGINAS (CADA SECCIÓN DE LA APP)
# ============================================

def pagina_registro_conductores():
    """Muestra el formulario de registro de conductores y la lista de conductores."""
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

def pagina_crear_envio():
    """Formulario para crear un nuevo envío (conductor obligatorio, cliente opcional)."""
    st.header("📦 Crear Nuevo Envío")
    with st.form("form_envio"):
        # Selector de conductores (obligatorio)
        conductores_lista = obtener_conductores()
        if conductores_lista:
            opciones = {f"{c['nombre']} (placa: {c['placa']})": c['id'] for c in conductores_lista}
            conductor_seleccionado = st.selectbox("Conductor", options=list(opciones.keys()))
            conductor_id = opciones[conductor_seleccionado]
        else:
            st.warning("Primero debes registrar al menos un conductor.")
            conductor_id = None

        # Selector de clientes (opcional)
        clientes_lista = obtener_clientes()
        if clientes_lista:
            opciones_cliente = {f"{c['nombre']} ({c.get('empresa', 'Sin empresa')})": c['id'] for c in clientes_lista}
            cliente_seleccionado = st.selectbox("Cliente (opcional)", options=["Ninguno"] + list(opciones_cliente.keys()))
            cliente_id = None if cliente_seleccionado == "Ninguno" else opciones_cliente[cliente_seleccionado]
        else:
            cliente_id = None

        origen = st.text_input("Origen")
        destino = st.text_input("Destino")
        submitted_envio = st.form_submit_button("Crear Envío")

        if submitted_envio and conductor_id:
            if origen and destino:
                ok, msg = guardar_envio(conductor_id, origen, destino, cliente_id)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Origen y destino son obligatorios")
        elif submitted_envio and not conductor_id:
            st.error("No hay conductores disponibles")

def pagina_registro_clientes():
    """Formulario para registrar un nuevo cliente."""
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

def pagina_panel_conductor():
    """Panel para que un conductor seleccione un envío y actualice su ubicación en un mapa."""
    st.header("🚛 Panel del Conductor")
    conductores = obtener_conductores()
    if not conductores:
        st.warning("No hay conductores registrados.")
        return

    nombres_conductores = [c["nombre"] for c in conductores]
    conductor_seleccionado_nombre = st.selectbox("Selecciona tu nombre", nombres_conductores)
    # Obtener el id del conductor seleccionado
    conductor_id = next(c["id"] for c in conductores if c["nombre"] == conductor_seleccionado_nombre)

    # Obtener envíos asignados a este conductor
    url_envios = f"{SUPABASE_URL}/rest/v1/envios?conductor_id=eq.{conductor_id}&select=*"
    response = requests.get(url_envios, headers=headers)
    if response.status_code != 200:
        st.error("Error al cargar los envíos")
        return
    envios = response.json()
    if not envios:
        st.info("No tienes envíos asignados.")
        return

    opciones_envio = {f"ID {e['id']} - {e['origen']} → {e['destino']} (estado: {e['estado']})": e for e in envios}
    envio_seleccionado_str = st.selectbox("Selecciona un envío", list(opciones_envio.keys()))
    envio = opciones_envio[envio_seleccionado_str]

    st.subheader("📍 Actualizar ubicación")
    lat_inicial = envio.get("lat") or 4.5709  # Coordenadas de Bogotá por defecto
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

def pagina_rastrear_envio():
    """Permite a un cliente (o cualquiera) buscar un envío por ID y ver su última ubicación."""
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

def login_register_page():
    """Pantalla de inicio de sesión y registro (se muestra cuando no hay usuario autenticado)."""
    st.title("🔐 Sistema de Logística")
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Ingresar")
            if submitted:
                ok, msg, token, uid, rol, nombre = iniciar_sesion(email, password)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.access_token = token
                    st.session_state.user_id = uid
                    st.session_state.rol = rol
                    st.session_state.user_email = email
                    st.session_state.user_nombre = nombre
                    st.rerun()
                else:
                    st.error(msg)

    with tab2:
        with st.form("register_form"):
            email_reg = st.text_input("Correo electrónico")
            password_reg = st.text_input("Contraseña", type="password")
            rol_reg = st.selectbox("Tipo de usuario", ["cliente", "conductor", "admin"])
            nombre_reg = st.text_input("Nombre completo")
            telefono_reg = st.text_input("Teléfono (opcional)")
            empresa_reg = st.text_input("Empresa (solo clientes, opcional)")
            submitted_reg = st.form_submit_button("Registrarse")
            if submitted_reg:
                if not email_reg or not password_reg or not nombre_reg:
                    st.warning("Correo, contraseña y nombre son obligatorios.")
                else:
                    ok, msg, uid = registrar_usuario(email_reg, password_reg, rol_reg, nombre_reg, telefono_reg, empresa_reg)
                    if ok:
                        st.success(msg)
                        st.info("Ahora puedes iniciar sesión.")
                    else:
                        st.error(msg)

# ============================================
# CONTROL DE ACCESO (AUTH) - PUNTO DE ENTRADA PRINCIPAL
# ============================================
# Si el usuario no ha iniciado sesión, mostramos la pantalla de login/registro.
# Si ya está autenticado, mostramos la barra lateral y las páginas según su rol.
if not st.session_state.authenticated:
    login_register_page()
else:
    # Barra lateral con información del usuario y botón de cierre de sesión
    st.sidebar.title(f"Bienvenido, {st.session_state.user_nombre} ({st.session_state.rol})")
    if st.sidebar.button("Cerrar sesión"):
        cerrar_sesion()

    st.sidebar.title("Navegación")

    # Construir menú de opciones según el rol del usuario autenticado
    rol = st.session_state.rol
    if rol == "admin":
        opciones = ["Registro de Conductores", "Crear Envío", "Registro de Clientes",
                    "Panel del Conductor", "Rastrear Envío"]
    elif rol == "cliente":
        opciones = ["Mis Envíos", "Rastrear Envío"]   # "Mis Envíos" aún por implementar
    elif rol == "conductor":
        opciones = ["Panel del Conductor"]
    else:
        opciones = []

    opcion = st.sidebar.radio("Ir a:", opciones)

    # Mostrar la página correspondiente según la opción seleccionada
    if opcion == "Registro de Conductores":
        pagina_registro_conductores()
    elif opcion == "Crear Envío":
        pagina_crear_envio()
    elif opcion == "Registro de Clientes":
        pagina_registro_clientes()
    elif opcion == "Panel del Conductor":
        pagina_panel_conductor()
    elif opcion == "Rastrear Envío":
        pagina_rastrear_envio()
    elif opcion == "Mis Envíos":
        st.info("Próximamente: lista de tus envíos")