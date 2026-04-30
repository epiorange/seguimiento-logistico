-- ============================================
-- ESQUEMA DE BASE DE DATOS - LOGÍSTICA COLOMBIA
-- Fecha: 2026-04-28
-- ============================================

-- Tabla: conductores
-- Almacena los transportistas registrados.
CREATE TABLE IF NOT EXISTS conductores (
    id BIGSERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    placa TEXT NOT NULL,
    telefono TEXT,
    fecha_registro TIMESTAMPTZ DEFAULT now()
);

-- Tabla: clientes
-- Empresas o personas que solicitan el transporte.
CREATE TABLE IF NOT EXISTS clientes (
    id BIGSERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    empresa TEXT,
    email TEXT UNIQUE,
    telefono TEXT,
    fecha_registro TIMESTAMPTZ DEFAULT now()
);

-- Tabla: envios
-- Cada envío asociado a un conductor y opcionalmente a un cliente.
CREATE TABLE IF NOT EXISTS envios (
    id BIGSERIAL PRIMARY KEY,
    conductor_id BIGINT NOT NULL REFERENCES conductores(id) ON DELETE RESTRICT,
    cliente_id BIGINT REFERENCES clientes(id) ON DELETE SET NULL,
    origen TEXT,
    destino TEXT,
    estado TEXT DEFAULT 'pendiente',
    lat FLOAT8,
    lng FLOAT8,
    fecha_creacion TIMESTAMPTZ DEFAULT now()
);

-- Índices sugeridos para mejorar el rendimiento de las consultas más comunes
CREATE INDEX IF NOT EXISTS idx_envios_conductor ON envios(conductor_id);
CREATE INDEX IF NOT EXISTS idx_envios_cliente ON envios(cliente_id);
CREATE INDEX IF NOT EXISTS idx_envios_estado ON envios(estado);

-- Comentarios sobre las tablas (opcional, pero útil para documentación)
COMMENT ON TABLE conductores IS 'Personas que ofrecen el servicio de transporte';
COMMENT ON TABLE clientes IS 'Empresas o individuos que necesitan enviar carga';
COMMENT ON TABLE envios IS 'Transacciones de carga que vinculan a un conductor con un cliente';