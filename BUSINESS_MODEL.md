# Modelo de Negocio - Logística Colombia

## 1. Segmentos de clientes
*   **Enfoque Principal**: Pequeños y medianos empresarios (PyMEs) y Transportistas independientes.
*   **Potencial Futuro**: Grandes empresas con operaciones logísticas.
*   **Validación**: Las PyMEs representan >90% del tejido empresarial colombiano[reference:8]. El mercado de transporte de carga mueve millones de toneladas anualmente[reference:9].

## 2. Propuesta de valor
*   **Trazabilidad Total** (Ya implementado): Seguimiento GPS en tiempo real para dar tranquilidad y control.
*   **Ecosistema de Confianza** (Próximo paso): Sistema de reputación, reseñas y documentación verificada de transportistas.
*   **Solidez Financiera** (Visión a futuro): Integración de pagos digitales (empezando con transferencias Bre-B / Cobre[reference:10]) con opciones de "paga después" (Buy Now, Pay Later) para gestionar la liquidez[reference:11].

## 3. Canales (Adquisición de Clientes)
*   **Ventas Directas (Cara a Cara)**: Estrategia principal para conseguir los primeros clientes. Consiste en ofrecer un periodo de prueba gratuito (1-2 meses) a empresas locales.
*   **Marketing de Contenidos**: Publicar resultados de los pilotos, guías y artículos en redes sociales (LinkedIn, Facebook) para construir autoridad y atraer clientes de manera orgánica.

## 4. Fuentes de ingresos
*   **Modelo Freemium (SaaS + Transaccional)** : El plan gratuito será la principal herramienta de adquisición de usuarios.
*   **Plan de Pago (Suscripción Mensual)**: Incluye funcionalidades avanzadas como reportes, multi-usuario, y la futura integración de pagos.
*   **Comisión por Transacción**: Para retener el valor desde el inicio, se aplicará una pequeña comisión (ej. 3-5%) a los envíos realizados en el plan gratuito, incentivando la migración al plan de suscripción.

## 5. Historial de decisiones y aprendizajes

#### 2026-04-23 - Definición de la Estrategia Comercial
*   **Decisión**: Se definió un enfoque dual en PyMEs y Transportistas Independientes.
*   **Decisión - Monetización**: Se adoptó un modelo Freemium con una capa SaaS y una capa transaccional.
*   **Investigación - Pagos**: Se identificó que el ecosistema de pagos digitales B2B en Colombia está en pleno despegue con la llegada de Bre-B. Se debe investigar a fondo la integración con Cobre, la plataforma pionera en habilitar pagos instantáneos para empresas de logística[reference:12].
*   **Investigación - Confianza**: Se determinó que construir un sistema robusto de reputación y verificación de documentos es más prioritario que implementar pagos online en esta fase.

### 2026-05-03 - Avance en modelo de negocio
- Se completa la gestión de clientes dentro de la plataforma.
- Cada envío ahora puede asociarse a un cliente, lo que permite:
  - Rastreo personalizado por cliente (futuro).
  - Segmentación de demanda y análisis de uso.
- Base técnica para futura autenticación (rol cliente).
### 2026-05-17 - Hito técnico: Autenticación y roles
- Se añade gestión de usuarios con roles (admin, conductor, cliente). Esto permite construir un sistema multi-tenant, base para:
  - Panel personalizado para cada cliente (ver solo sus envíos).
  - Seguridad en las peticiones a futuro (usando tokens JWT).
  - Modelo de negocio: diferenciar funcionalidades por tipo de usuario (freemium, planes por rol).