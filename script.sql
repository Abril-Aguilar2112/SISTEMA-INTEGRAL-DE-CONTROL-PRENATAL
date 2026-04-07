-- =========================================
-- 🔥 LIMPIEZA
-- =========================================
DROP TABLE IF EXISTS mensaje CASCADE;
DROP TABLE IF EXISTS inasistencia CASCADE;
DROP TABLE IF EXISTS cita CASCADE;
DROP TABLE IF EXISTS consulta CASCADE;
DROP TABLE IF EXISTS historial_clinico CASCADE;
DROP TABLE IF EXISTS notificacion CASCADE;
DROP TABLE IF EXISTS sintoma CASCADE;
DROP TABLE IF EXISTS reporte CASCADE;
DROP TABLE IF EXISTS censo_reporte CASCADE;
DROP TABLE IF EXISTS unidad_salud CASCADE;
DROP TABLE IF EXISTS control_prenatal CASCADE;
DROP TABLE IF EXISTS paciente CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;

DROP TYPE IF EXISTS rol_usuario CASCADE;
DROP TYPE IF EXISTS estado_cita CASCADE;
DROP TYPE IF EXISTS estado_notificacion CASCADE;
DROP TYPE IF EXISTS nivel_riesgo_enum CASCADE;


-- =========================================
-- 🧠 ENUMS
-- =========================================
CREATE TYPE rol_usuario AS ENUM (
  'trabajo_social',
  'enfermera',
  'director_general',
  'paciente',
  'medico'
);

CREATE TYPE estado_cita AS ENUM (
  'pendiente',
  'confirmada',
  'cancelada',
  'completada'
);

CREATE TYPE estado_notificacion AS ENUM (
  'no_leida',
  'leida'
);

CREATE TYPE nivel_riesgo_enum AS ENUM (
  'bajo',
  'medio',
  'alto'
);


-- =========================================
-- 👤 USUARIO
-- =========================================
CREATE TABLE usuario (
  id_usuario SERIAL PRIMARY KEY,
  auth_id    UUID   UNIQUE NOT NULL,
  nombre     TEXT   NOT NULL,
  correo     TEXT   UNIQUE NOT NULL,
  rol        rol_usuario NOT NULL DEFAULT 'paciente'
);


-- =========================================
-- 🤰 PACIENTE
-- =========================================
CREATE TABLE paciente (
  id_paciente       SERIAL PRIMARY KEY,
  id_usuario        INTEGER UNIQUE,

  -- Datos personales
  nombre            TEXT    NOT NULL,
  edad              INTEGER CHECK (edad > 0),
  telefono          TEXT,
  curp              TEXT    UNIQUE,
  colonia           TEXT,
  lengua_indigena   TEXT,

  -- Obstétrico básico
  semanas_gestacion INTEGER CHECK (semanas_gestacion >= 0),
  nivel_riesgo      nivel_riesgo_enum DEFAULT 'bajo',

  CONSTRAINT fk_paciente_usuario
    FOREIGN KEY (id_usuario)
    REFERENCES usuario(id_usuario)
    ON DELETE CASCADE
);


-- =========================================
-- 🏥 UNIDAD DE SALUD
-- =========================================
CREATE TABLE unidad_salud (
  id_unidad       SERIAL PRIMARY KEY,
  id_paciente     INTEGER UNIQUE NOT NULL
                    REFERENCES paciente(id_paciente) ON DELETE CASCADE,

  region          TEXT,
  clues_imb       TEXT,
  municipio       TEXT,
  tipo_localidad  TEXT CHECK (tipo_localidad IN ('Urbana', 'Rural')),
  nombre_unidad   TEXT,
  zona_servicios  TEXT,
  no_consecutivo  TEXT,

  fecha_registro  TIMESTAMP DEFAULT NOW()
);


-- =========================================
-- 🩺 CONTROL PRENATAL
-- =========================================
CREATE TABLE control_prenatal (
  id_control      SERIAL PRIMARY KEY,
  id_paciente     INTEGER UNIQUE
                    REFERENCES paciente(id_paciente) ON DELETE CASCADE,

  -- Fechas clave
  fur                   DATE,
  fpp                   DATE,
  semanas_gestacion     INTEGER,
  fecha_ingreso_cpn     DATE,
  fecha_ultima_atencion DATE,

  -- Antecedentes obstétricos
  gestas    INTEGER DEFAULT 0,
  partos    INTEGER DEFAULT 0,
  cesareas  INTEGER DEFAULT 0,
  abortos   INTEGER DEFAULT 0,

  -- Riesgo y seguimiento
  riesgo_obstetrico  TEXT,
  riesgo_social      TEXT,
  factores_riesgo    TEXT,
  consultas_otorgadas INTEGER,
  estado_salud       TEXT,

  fecha_registro TIMESTAMP DEFAULT NOW()
);


-- =========================================
-- 📊 CENSO / REPORTE MENSUAL
-- =========================================
CREATE TABLE censo_reporte (
  id_censo              SERIAL PRIMARY KEY,
  id_paciente           INTEGER UNIQUE NOT NULL
                          REFERENCES paciente(id_paciente) ON DELETE CASCADE,

  mes_reporte           TEXT,
  fecha_reporte         DATE,
  semana_epidemiologica INTEGER CHECK (semana_epidemiologica BETWEEN 1 AND 53),

  fecha_registro        TIMESTAMP DEFAULT NOW()
);


-- =========================================
-- 📅 CITA
-- =========================================
CREATE TABLE cita (
  id_cita     SERIAL PRIMARY KEY,
  id_paciente INTEGER NOT NULL
                REFERENCES paciente(id_paciente) ON DELETE CASCADE,
  fecha       DATE    NOT NULL,
  hora        TIME    NOT NULL,
  estado      estado_cita DEFAULT 'pendiente'
);


-- =========================================
-- ❌ INASISTENCIA
-- =========================================
CREATE TABLE inasistencia (
  id_inasistencia SERIAL PRIMARY KEY,
  id_cita         INTEGER NOT NULL
                    REFERENCES cita(id_cita) ON DELETE CASCADE,
  motivo          TEXT,
  justificada     BOOLEAN DEFAULT FALSE,
  fecha           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- =========================================
-- 🩺 CONSULTA
-- =========================================
CREATE TABLE consulta (
  id_consulta SERIAL PRIMARY KEY,
  id_paciente INTEGER NOT NULL
                REFERENCES paciente(id_paciente) ON DELETE CASCADE,
  id_usuario  INTEGER
                REFERENCES usuario(id_usuario) ON DELETE SET NULL,
  fecha       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  diagnostico TEXT,
  tratamiento TEXT
);


-- =========================================
-- 📋 HISTORIAL CLÍNICO
-- =========================================
CREATE TABLE historial_clinico (
  id_historial  SERIAL PRIMARY KEY,
  id_paciente   INTEGER UNIQUE NOT NULL
                  REFERENCES paciente(id_paciente) ON DELETE CASCADE,
  antecedentes  TEXT,
  observaciones TEXT
);


-- =========================================
-- 🔔 NOTIFICACION
-- =========================================
CREATE TABLE notificacion (
  id_notificacion SERIAL PRIMARY KEY,
  id_paciente     INTEGER NOT NULL
                    REFERENCES paciente(id_paciente) ON DELETE CASCADE,
  mensaje         TEXT    NOT NULL,
  fecha           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  estado          estado_notificacion DEFAULT 'no_leida'
);


-- =========================================
-- 🤒 SINTOMA
-- =========================================
CREATE TABLE sintoma (
  id_sintoma  SERIAL PRIMARY KEY,
  id_paciente INTEGER NOT NULL
                REFERENCES paciente(id_paciente) ON DELETE CASCADE,
  descripcion TEXT    NOT NULL,
  intensidad  TEXT,
  fecha       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- =========================================
-- 📊 REPORTE
-- =========================================
CREATE TABLE reporte (
  id_reporte SERIAL PRIMARY KEY,
  id_usuario INTEGER
               REFERENCES usuario(id_usuario) ON DELETE SET NULL,
  fecha      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  tipo       TEXT,
  datos      JSONB
);


-- =========================================
-- 💬 MENSAJE
-- =========================================
CREATE TABLE mensaje (
  id_mensaje  SERIAL PRIMARY KEY,
  emisor_id   INTEGER REFERENCES usuario(id_usuario),
  receptor_id INTEGER REFERENCES usuario(id_usuario),
  contenido   TEXT    NOT NULL,
  fecha       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  leido       BOOLEAN DEFAULT FALSE
);


-- =========================================
-- ⚡ ÍNDICES
-- =========================================
CREATE INDEX idx_paciente_usuario      ON paciente(id_usuario);
CREATE INDEX idx_cita_fecha            ON cita(fecha);
CREATE INDEX idx_consulta_paciente     ON consulta(id_paciente);
CREATE INDEX idx_unidad_paciente       ON unidad_salud(id_paciente);
CREATE INDEX idx_censo_paciente        ON censo_reporte(id_paciente);
CREATE INDEX idx_control_paciente      ON control_prenatal(id_paciente);
CREATE INDEX idx_notificacion_paciente ON notificacion(id_paciente);


-- =========================================
-- ⚙️ TRIGGER: CALCULAR NIVEL DE RIESGO
-- Se dispara al insertar o actualizar paciente.
-- Toma semanas desde control_prenatal si existe,
-- si no, usa paciente.semanas_gestacion.
-- =========================================
CREATE OR REPLACE FUNCTION calcular_riesgo()
RETURNS TRIGGER AS $$
DECLARE
  semanas INT;
BEGIN
  SELECT cp.semanas_gestacion INTO semanas
  FROM control_prenatal cp
  WHERE cp.id_paciente = NEW.id_paciente
  LIMIT 1;

  IF semanas IS NULL THEN
    semanas := NEW.semanas_gestacion;
  END IF;

  IF semanas >= 35 THEN
    NEW.nivel_riesgo := 'alto';
  ELSIF semanas >= 20 THEN
    NEW.nivel_riesgo := 'medio';
  ELSE
    NEW.nivel_riesgo := 'bajo';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_riesgo
BEFORE INSERT OR UPDATE ON paciente
FOR EACH ROW
EXECUTE FUNCTION calcular_riesgo();


-- =========================================
-- 🔔 TRIGGER: NOTIFICAR NUEVA CITA
-- =========================================
CREATE OR REPLACE FUNCTION notificar_cita()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO notificacion (id_paciente, mensaje)
  VALUES (
    NEW.id_paciente,
    'Tienes una nueva cita el ' || NEW.fecha
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_notificacion_cita
AFTER INSERT ON cita
FOR EACH ROW
EXECUTE FUNCTION notificar_cita();


-- =========================================
-- 💾 FUNCIÓN: REGISTRAR PACIENTE COMPLETO
-- Inserta en: paciente, control_prenatal,
-- historial_clinico, unidad_salud,
-- censo_reporte, notificacion
-- =========================================
CREATE OR REPLACE FUNCTION registrar_paciente_completo(
  -- Datos personales
  p_nombre            TEXT,
  p_edad              INT,
  p_telefono          TEXT    DEFAULT NULL,
  p_curp              TEXT    DEFAULT NULL,
  p_colonia           TEXT    DEFAULT NULL,
  p_lengua_indigena   TEXT    DEFAULT NULL,

  -- Control prenatal
  p_semanas           INT     DEFAULT 0,
  p_fur               DATE    DEFAULT NULL,
  p_fpp               DATE    DEFAULT NULL,
  p_riesgo_obstetrico TEXT    DEFAULT NULL,
  p_riesgo_social     TEXT    DEFAULT NULL,
  p_factores          TEXT    DEFAULT NULL,
  p_consultas         INT     DEFAULT 0,
  p_estado_salud      TEXT    DEFAULT NULL,

  -- Antecedentes obstétricos
  p_gestas                INT  DEFAULT 0,
  p_partos                INT  DEFAULT 0,
  p_cesareas              INT  DEFAULT 0,
  p_abortos               INT  DEFAULT 0,
  p_fecha_ultima_atencion DATE DEFAULT NULL,
  p_fecha_ingreso_cpn     DATE DEFAULT NULL,

  -- Historial clínico
  p_antecedentes  TEXT DEFAULT NULL,
  p_observaciones TEXT DEFAULT NULL,

  -- Unidad de salud
  p_region          TEXT DEFAULT NULL,
  p_clues_imb       TEXT DEFAULT NULL,
  p_municipio       TEXT DEFAULT NULL,
  p_tipo_localidad  TEXT DEFAULT NULL,
  p_nombre_unidad   TEXT DEFAULT NULL,
  p_zona_servicios  TEXT DEFAULT NULL,
  p_no_consecutivo  TEXT DEFAULT NULL,

  -- Censo / reporte
  p_mes_reporte           TEXT    DEFAULT NULL,
  p_fecha_reporte         DATE    DEFAULT NULL,
  p_semana_epidemiologica INT     DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
  v_id_paciente INT;
BEGIN

  -- Validaciones básicas
  IF p_nombre IS NULL OR TRIM(p_nombre) = '' THEN
    RETURN json_build_object('ok', false, 'error', 'El nombre es obligatorio');
  END IF;

  IF p_edad IS NULL OR p_edad <= 0 THEN
    RETURN json_build_object('ok', false, 'error', 'Edad inválida');
  END IF;

  -- 1. Insertar paciente
  INSERT INTO paciente (
    nombre, edad, telefono, semanas_gestacion,
    curp, colonia, lengua_indigena
  )
  VALUES (
    p_nombre, p_edad, p_telefono, p_semanas,
    p_curp, p_colonia, p_lengua_indigena
  )
  RETURNING id_paciente INTO v_id_paciente;

  -- 2. Control prenatal
  INSERT INTO control_prenatal (
    id_paciente,
    fur, fpp, semanas_gestacion,
    fecha_ingreso_cpn, fecha_ultima_atencion,
    gestas, partos, cesareas, abortos,
    riesgo_obstetrico, riesgo_social,
    factores_riesgo, consultas_otorgadas, estado_salud
  )
  VALUES (
    v_id_paciente,
    p_fur, p_fpp, p_semanas,
    p_fecha_ingreso_cpn, p_fecha_ultima_atencion,
    p_gestas, p_partos, p_cesareas, p_abortos,
    p_riesgo_obstetrico, p_riesgo_social,
    p_factores, p_consultas, p_estado_salud
  );

  -- 3. Historial clínico
  INSERT INTO historial_clinico (id_paciente, antecedentes, observaciones)
  VALUES (v_id_paciente, p_antecedentes, p_observaciones);

  -- 4. Unidad de salud
  INSERT INTO unidad_salud (
    id_paciente,
    region, clues_imb, municipio, tipo_localidad,
    nombre_unidad, zona_servicios, no_consecutivo
  )
  VALUES (
    v_id_paciente,
    p_region, p_clues_imb, p_municipio, p_tipo_localidad,
    p_nombre_unidad, p_zona_servicios, p_no_consecutivo
  );

  -- 5. Censo / reporte
  INSERT INTO censo_reporte (
    id_paciente,
    mes_reporte, fecha_reporte, semana_epidemiologica
  )
  VALUES (
    v_id_paciente,
    p_mes_reporte, p_fecha_reporte, p_semana_epidemiologica
  );

  -- 6. Notificación inicial
  INSERT INTO notificacion (id_paciente, mensaje)
  VALUES (v_id_paciente, 'Paciente registrada correctamente en el sistema');

  RETURN json_build_object('ok', true, 'id_paciente', v_id_paciente);

EXCEPTION
  WHEN unique_violation THEN
    RETURN json_build_object('ok', false, 'error', 'La paciente ya existe (CURP o registro duplicado)');
  WHEN foreign_key_violation THEN
    RETURN json_build_object('ok', false, 'error', 'Error de integridad de datos');
  WHEN check_violation THEN
    RETURN json_build_object('ok', false, 'error', 'Un valor está fuera del rango permitido');
  WHEN OTHERS THEN
    RETURN json_build_object('ok', false, 'error', SQLERRM);
END;
$$ LANGUAGE plpgsql;


-- =========================================
-- 📈 FUNCIÓN: REPORTE MENSUAL
-- =========================================
CREATE OR REPLACE FUNCTION reporte_mensual()
RETURNS TABLE (
  total_citas         INTEGER,
  total_inasistencias INTEGER
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    (SELECT COUNT(*) FROM cita)::INTEGER,
    (SELECT COUNT(*) FROM inasistencia)::INTEGER;
END;
$$ LANGUAGE plpgsql;


-- =========================================
-- 📊 VISTA: DASHBOARD GENERAL (conteos por riesgo)
-- =========================================
CREATE VIEW dashboard_general AS
SELECT
  COUNT(*) FILTER (WHERE nivel_riesgo = 'alto')  AS alto_riesgo,
  COUNT(*) FILTER (WHERE nivel_riesgo = 'medio') AS medio_riesgo,
  COUNT(*) FILTER (WHERE nivel_riesgo = 'bajo')  AS bajo_riesgo,
  COUNT(*)                                        AS total
FROM paciente;


-- =========================================
-- 📊 VISTA: DASHBOARD STATS (tarjetas resumen)
-- =========================================
CREATE VIEW dashboard_stats AS
SELECT
  (SELECT COUNT(*) FROM paciente)                                AS total_pacientes,
  (SELECT COUNT(*) FROM cita        WHERE estado='pendiente')    AS citas_programadas,
  (SELECT COUNT(*) FROM paciente    WHERE nivel_riesgo='alto')   AS alto_riesgo,
  (SELECT COUNT(*) FROM inasistencia)                            AS inasistencias;

-- =========================================
-- 📊 VISTA: ACTIVIDAD RECIENTE
-- =========================================
CREATE VIEW actividad_reciente AS
  SELECT c.fecha, p.nombre, 'Cita programada'       AS accion, c.estado::text AS estado
  FROM cita c
  JOIN paciente p ON p.id_paciente = c.id_paciente

UNION ALL

  SELECT i.fecha, p.nombre, 'Inasistencia reportada',
    CASE WHEN i.justificada THEN 'justificada' ELSE 'pendiente' END
  FROM inasistencia i
  JOIN cita      c ON c.id_cita     = i.id_cita
  JOIN paciente  p ON p.id_paciente = c.id_paciente

UNION ALL

  SELECT con.fecha, p.nombre, 'Consulta registrada', 'completado'
  FROM consulta con
  JOIN paciente p ON p.id_paciente = con.id_paciente

ORDER BY fecha DESC
LIMIT 10;


-- =========================================
-- 📊 VISTA: ESTADÍSTICAS DASHBOARD (porcentajes)
-- =========================================
CREATE OR REPLACE VIEW estadisticas_dashboard AS
SELECT
  (
    SELECT ROUND(
      (COUNT(*) FILTER (WHERE nivel_riesgo = 'alto') * 100.0) /
      NULLIF(COUNT(*), 0), 1)
    FROM paciente
  ) AS pct_alto_riesgo,

  ROUND(
    (COUNT(*) FILTER (WHERE estado = 'completada') * 100.0) /
    NULLIF(COUNT(*), 0), 1
  ) AS tasa_asistencia,

  ROUND(
    (COUNT(*) FILTER (WHERE estado = 'pendiente') * 100.0) /
    NULLIF(COUNT(*), 0), 1
  ) AS pendientes_seguimiento,

  ROUND(
    (SELECT COUNT(*) FROM consulta) * 100.0 /
    NULLIF((SELECT COUNT(*) FROM cita), 0), 1
  ) AS controles_completados

FROM cita;


-- =========================================
-- 📊 VISTA: PACIENTES DASHBOARD (listado completo)
-- =========================================
CREATE OR REPLACE VIEW pacientes_dashboard AS
SELECT
  p.id_paciente,
  p.nombre,
  p.curp,
  p.edad,
  p.telefono,
  p.colonia,
  p.lengua_indigena,
  p.nivel_riesgo,

  COALESCE(cp.semanas_gestacion, p.semanas_gestacion) AS semanas_gestacion,
  cp.fpp,
  cp.gestas,
  cp.partos,
  cp.cesareas,
  cp.abortos,
  cp.fecha_ingreso_cpn,
  cp.fecha_ultima_atencion,
  cp.riesgo_obstetrico,
  cp.estado_salud,

  us.municipio,
  us.region,
  us.nombre_unidad,
  us.clues_imb,

  cr.mes_reporte,
  cr.semana_epidemiologica,

  MAX(c.fecha) AS ultima_consulta

FROM paciente p
LEFT JOIN control_prenatal cp ON cp.id_paciente = p.id_paciente
LEFT JOIN unidad_salud     us ON us.id_paciente = p.id_paciente
LEFT JOIN censo_reporte    cr ON cr.id_paciente = p.id_paciente
LEFT JOIN consulta          c ON  c.id_paciente = p.id_paciente

GROUP BY
  p.id_paciente, p.nombre, p.curp, p.edad,
  p.telefono, p.colonia, p.lengua_indigena, p.nivel_riesgo,
  cp.semanas_gestacion, cp.fpp, cp.gestas, cp.partos,
  cp.cesareas, cp.abortos, cp.fecha_ingreso_cpn,
  cp.fecha_ultima_atencion, cp.riesgo_obstetrico, cp.estado_salud,
  us.municipio, us.region, us.nombre_unidad, us.clues_imb,
  cr.mes_reporte, cr.semana_epidemiologica;