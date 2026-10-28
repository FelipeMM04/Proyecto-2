-- ====================================================================
-- ESQUEMA DDL REFINADO: DATA WAREHOUSE TURISMO Y DESARROLLO (ODS 8)
-- Motor Target: PostgreSQL 15+
-- Base de Datos Target: dw_turismo_ods8_v2
-- Sección de Rúbrica: 15. Data Warehouse Implementation and Load
-- ====================================================================

-- Eliminar tablas en orden inverso de dependencias
DROP TABLE IF EXISTS fact_turismo_anual CASCADE;
DROP TABLE IF EXISTS fact_indicadores_departamentales CASCADE;
DROP TABLE IF EXISTS dim_ubicacion CASCADE;
DROP TABLE IF EXISTS dim_categoria CASCADE;
DROP TABLE IF EXISTS dim_prestador CASCADE;
DROP TABLE IF EXISTS dim_tiempo CASCADE;

-- 1. Dimensión Ubicación Enriquecida
CREATE TABLE dim_ubicacion (
    codigo_municipio INT NOT NULL,
    municipio VARCHAR(150) NOT NULL,
    codigo_departamento INT NOT NULL,
    departamento VARCHAR(150) NOT NULL,
    poblacion_total_estimada INT DEFAULT 0,
    PRIMARY KEY (codigo_municipio)
);

-- 2. Dimensión Categoría (Surrogate Key)
CREATE TABLE dim_categoria (
    id_categoria SERIAL PRIMARY KEY,
    categoria VARCHAR(150) NOT NULL,
    sub_categoria VARCHAR(150) NOT NULL
);

-- 3. Dimensión Prestador
CREATE TABLE dim_prestador (
    codigo_rnt INT NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    nit VARCHAR(50) NOT NULL,
    estado_rnt VARCHAR(50) NOT NULL,
    PRIMARY KEY (codigo_rnt)
);

-- 4. Dimensión Tiempo
CREATE TABLE dim_tiempo (
    anio INT NOT NULL,
    PRIMARY KEY (anio)
);

-- 5. Tabla de Hechos Principal: Operación Turística Anual
CREATE TABLE fact_turismo_anual (
    id_fact SERIAL PRIMARY KEY,
    codigo_rnt INT NOT NULL,
    codigo_municipio INT NOT NULL,
    id_categoria INT NOT NULL,
    anio INT NOT NULL,
    numero_de_habitaciones INT NOT NULL DEFAULT 0,
    numero_de_camas INT NOT NULL DEFAULT 0,
    numero_de_empleados INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_fact_prestador FOREIGN KEY (codigo_rnt) REFERENCES dim_prestador (codigo_rnt),
    CONSTRAINT fk_fact_ubicacion FOREIGN KEY (codigo_municipio) REFERENCES dim_ubicacion (codigo_municipio),
    CONSTRAINT fk_fact_categoria FOREIGN KEY (id_categoria) REFERENCES dim_categoria (id_categoria),
    CONSTRAINT fk_fact_tiempo FOREIGN KEY (anio) REFERENCES dim_tiempo (anio)
);

-- 6. Tabla de Hechos Secundaria: Indicadores Económicos Integrados (API DANE)
CREATE TABLE fact_indicadores_departamentales (
    id_indicador SERIAL PRIMARY KEY,
    codigo_departamento INT NOT NULL,
    anio INT NOT NULL,
    total_empleo_formal_dane BIGINT NOT NULL,
    CONSTRAINT fk_ind_tiempo FOREIGN KEY (anio) REFERENCES dim_tiempo (anio)
);

-- Índices de Rendimiento para Consultas de Dashboard (R1-R7)
CREATE INDEX idx_fact_turismo_ubicacion ON fact_turismo_anual(codigo_municipio);
CREATE INDEX idx_fact_turismo_categoria ON fact_turismo_anual(id_categoria);
CREATE INDEX idx_fact_turismo_tiempo ON fact_turismo_anual(anio);