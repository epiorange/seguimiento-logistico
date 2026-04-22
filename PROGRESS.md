# Bitácora de desarrollo - Sistema de Logística Colombia

## 2026-04-07 (Configuración inicial)
- Instalación de Python, VS Code, Git.
- Creación de entorno virtual `venv` y activación.
- Instalación de librerías: `streamlit`, `requests`.
- Creación de cuenta en Supabase y proyecto `seguimiento-logistico`.
- Creación de tabla `conductores` con columnas: id (PK), nombre, placa, telefono, fecha_registro.
- Desactivado RLS para pruebas.

## 2026-04-08 (Primera versión de la app)
- Archivo `app.py` con formulario de registro de conductores.
- Conexión a Supabase usando `requests` (POST y GET).
- Listado de conductores en tabla interactiva.

## 2026-04-11 (Tabla envíos y formulario)
- Creación de tabla `envios` con columnas: id (PK), conductor_id, origen, destino, estado, lat, lng, fecha_creacion.
- Agregada columna `cliente_nombre` (luego eliminada por simplicidad).
- Formulario para crear nuevos envíos asociados a conductores existentes.
- Corrección de errores 400 y 404 (nombres de columnas, indentación, espacio en `" destino"`).

## 2026-04-12 (Reorganización de la interfaz y Git)
- Implementada barra lateral con opciones: Registro de Conductores, Crear Envío, Panel del Conductor, Rastrear Envío.
- Movido el código de formularios dentro de los bloques `if` correspondientes.
- Inicializado repositorio Git local.
- Configurado `user.name` y `user.email`.
- Primer commit: "Versión inicial: registro de conductores y creación de envíos".
- Conectado con repositorio remoto en GitHub (`epiorange/seguimiento-logistico`).
- Autenticación con token y push exitoso.
- Segundo commit: "Agregada estructura de barra lateral y preparación para mapas".

## 2026-04-13 (Pendiente - mapas)
- Instalar `folium`, `streamlit-folium`, `pandas`.
- Implementar código en **Panel del Conductor**:
  - Selección de conductor y envío.
  - Mapa interactivo para actualizar ubicación (lat/lng en Supabase).
- Implementar código en **Rastrear Envío**:
  - Búsqueda por ID de envío.
  - Visualización de última ubicación en mapa.

  ## 2026-04-23 (Sprint 2 - Mapas completado)
- Implementado **Panel del Conductor**:
  - Selección de conductor y envío.
  - Mapa interactivo (Folium) para actualizar ubicación.
  - Corrección de error 204 (ahora acepta 200 y 204 como éxito).
- Implementado **Rastreo de Envío**:
  - Búsqueda por ID de envío.
  - Visualización de última ubicación en mapa.
- Todo el sistema funciona correctamente: registro de conductores, creación de envíos, actualización de ubicación y rastreo

## Próximos pasos (Sprint 3)
- [ ] Probar mapas y corregir errores.
- [ ] Agregar notificaciones por WhatsApp (Twilio).
- [ ] Autenticación de usuarios (login).
- [ ] Mejora de diseño y reportes.