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
  'inasistencia',
  'reprogramada'
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

CREATE TYPE observacion_inasistencia AS ENUM (
  'Se le agendará nueva cita',
  'Se canalizará a trabajo social',
  'Se dará de baja temporalmente',
  'Sin acción requerida'
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
  id_usuario INT NOT NULL,
  area TEXT NOT NULL,
  fecha       DATE    NOT NULL,
  hora        TIME    NOT NULL,
  estado      estado_cita DEFAULT 'pendiente',
  observaciones TEXT,
  FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
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
  observacion_ts observacion_inasistencia,
  mensaje_seguimiento TEXT,
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
  fecha      DATE DEFAULT current_date,
  periodo_inicio DATE NOT NULL,
  periodo_fin DATE NOT NULL,
  generado_por rol_usuario NOT NULL,
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
-- 💾 FUNCIÓN: ACTUALIZAR PACIENTE 
-- actualiza en: paciente, control_prenatal,
-- unidad_salud, notificacion, censo_reporte
-- =========================================
CREATE OR REPLACE FUNCTION actualizar_paciente(
  -- Identificador obligatorio
  p_id_paciente       INT,

  -- Datos personales
  p_nombre            TEXT    DEFAULT NULL,
  p_edad              INT     DEFAULT NULL,
  p_telefono          TEXT    DEFAULT NULL,
  p_curp              TEXT    DEFAULT NULL,
  p_colonia           TEXT    DEFAULT NULL,
  p_lengua_indigena   TEXT    DEFAULT NULL,

  -- Control prenatal
  p_fur               DATE    DEFAULT NULL,
  p_fpp               DATE    DEFAULT NULL,
  p_semanas           INT     DEFAULT NULL,
  p_fecha_ingreso_cpn DATE    DEFAULT NULL,
  p_fecha_ultima_atencion DATE DEFAULT NULL,
  p_gestas            INT     DEFAULT NULL,
  p_partos            INT     DEFAULT NULL,
  p_cesareas          INT     DEFAULT NULL,
  p_abortos           INT     DEFAULT NULL,
  p_riesgo_obstetrico TEXT    DEFAULT NULL,
  p_riesgo_social     TEXT    DEFAULT NULL,
  p_factores          TEXT    DEFAULT NULL,
  p_consultas         INT     DEFAULT NULL,
  p_estado_salud      TEXT    DEFAULT NULL,

  -- Unidad de salud
  p_region            TEXT    DEFAULT NULL,
  p_clues_imb         TEXT    DEFAULT NULL,
  p_municipio         TEXT    DEFAULT NULL,
  p_tipo_localidad    TEXT    DEFAULT NULL,
  p_nombre_unidad     TEXT    DEFAULT NULL,
  p_zona_servicios    TEXT    DEFAULT NULL,
  p_no_consecutivo    TEXT    DEFAULT NULL,

  -- Censo / reporte
  p_mes_reporte           TEXT    DEFAULT NULL,
  p_fecha_reporte         DATE    DEFAULT NULL,
  p_semana_epidemiologica INT     DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
  v_existe BOOLEAN;
BEGIN

-- ===========================================
-- FUNCION: OBTENER CITA POR id
-- ===========================================
CREATE OR REPLACE FUNCTION get_cita_by_id(p_id INT)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'id_cita', id_cita,
        'fecha', fecha,
        'hora', hora,
        'estado', estado,
        'area', area,
        'id_paciente', id_paciente,
        'paciente', paciente,
        'medico', medico
    )
    INTO result
    FROM vista_cita
    WHERE id_cita = p_id;

    IF result IS NULL THEN
        RETURN json_build_object(
            'ok', false,
            'error', 'Cita no encontrada'
        );
    END IF;

    RETURN json_build_object(
        'ok', true,
        'data', result
    );
END;
$$ LANGUAGE plpgsql;

  -- =========================================
  -- 👩 ACTUALIZAR PACIENTE
  -- Solo actualiza los campos que vienen (no NULL)
  -- =========================================
  UPDATE paciente SET
    nombre          = COALESCE(p_nombre,          nombre),
    edad            = COALESCE(p_edad,             edad),
    telefono        = COALESCE(p_telefono,         telefono),
    curp            = COALESCE(p_curp,             curp),
    colonia         = COALESCE(p_colonia,          colonia),
    lengua_indigena = COALESCE(p_lengua_indigena,  lengua_indigena),
    semanas_gestacion = COALESCE(p_semanas,        semanas_gestacion)
  WHERE id_paciente = p_id_paciente;

  -- =========================================
  -- 🩺 ACTUALIZAR CONTROL PRENATAL
  -- Upsert: actualiza si existe, inserta si no
  -- =========================================
  INSERT INTO control_prenatal (
    id_paciente,
    fur, fpp, semanas_gestacion,
    fecha_ingreso_cpn, fecha_ultima_atencion,
    gestas, partos, cesareas, abortos,
    riesgo_obstetrico, riesgo_social,
    factores_riesgo, consultas_otorgadas, estado_salud
  )
  VALUES (
    p_id_paciente,
    p_fur, p_fpp, p_semanas,
    p_fecha_ingreso_cpn, p_fecha_ultima_atencion,
    p_gestas, p_partos, p_cesareas, p_abortos,
    p_riesgo_obstetrico, p_riesgo_social,
    p_factores, p_consultas, p_estado_salud
  )
  ON CONFLICT (id_paciente) DO UPDATE SET
    fur                   = COALESCE(EXCLUDED.fur,                   control_prenatal.fur),
    fpp                   = COALESCE(EXCLUDED.fpp,                   control_prenatal.fpp),
    semanas_gestacion     = COALESCE(EXCLUDED.semanas_gestacion,     control_prenatal.semanas_gestacion),
    fecha_ingreso_cpn     = COALESCE(EXCLUDED.fecha_ingreso_cpn,     control_prenatal.fecha_ingreso_cpn),
    fecha_ultima_atencion = COALESCE(EXCLUDED.fecha_ultima_atencion, control_prenatal.fecha_ultima_atencion),
    gestas                = COALESCE(EXCLUDED.gestas,                control_prenatal.gestas),
    partos                = COALESCE(EXCLUDED.partos,                control_prenatal.partos),
    cesareas              = COALESCE(EXCLUDED.cesareas,              control_prenatal.cesareas),
    abortos               = COALESCE(EXCLUDED.abortos,               control_prenatal.abortos),
    riesgo_obstetrico     = COALESCE(EXCLUDED.riesgo_obstetrico,     control_prenatal.riesgo_obstetrico),
    riesgo_social         = COALESCE(EXCLUDED.riesgo_social,         control_prenatal.riesgo_social),
    factores_riesgo       = COALESCE(EXCLUDED.factores_riesgo,       control_prenatal.factores_riesgo),
    consultas_otorgadas   = COALESCE(EXCLUDED.consultas_otorgadas,   control_prenatal.consultas_otorgadas),
    estado_salud          = COALESCE(EXCLUDED.estado_salud,          control_prenatal.estado_salud);

  -- =========================================
  -- 🏥 ACTUALIZAR UNIDAD DE SALUD
  -- =========================================
  INSERT INTO unidad_salud (
    id_paciente,
    region, clues_imb, municipio, tipo_localidad,
    nombre_unidad, zona_servicios, no_consecutivo
  )
  VALUES (
    p_id_paciente,
    p_region, p_clues_imb, p_municipio, p_tipo_localidad,
    p_nombre_unidad, p_zona_servicios, p_no_consecutivo
  )
  ON CONFLICT (id_paciente) DO UPDATE SET
    region          = COALESCE(EXCLUDED.region,          unidad_salud.region),
    clues_imb       = COALESCE(EXCLUDED.clues_imb,       unidad_salud.clues_imb),
    municipio       = COALESCE(EXCLUDED.municipio,       unidad_salud.municipio),
    tipo_localidad  = COALESCE(EXCLUDED.tipo_localidad,  unidad_salud.tipo_localidad),
    nombre_unidad   = COALESCE(EXCLUDED.nombre_unidad,   unidad_salud.nombre_unidad),
    zona_servicios  = COALESCE(EXCLUDED.zona_servicios,  unidad_salud.zona_servicios),
    no_consecutivo  = COALESCE(EXCLUDED.no_consecutivo,  unidad_salud.no_consecutivo);

  -- =========================================
  -- 📊 ACTUALIZAR CENSO / REPORTE
  -- =========================================
  INSERT INTO censo_reporte (
    id_paciente,
    mes_reporte, fecha_reporte, semana_epidemiologica
  )
  VALUES (
    p_id_paciente,
    p_mes_reporte, p_fecha_reporte, p_semana_epidemiologica
  )
  ON CONFLICT (id_paciente) DO UPDATE SET
    mes_reporte           = COALESCE(EXCLUDED.mes_reporte,           censo_reporte.mes_reporte),
    fecha_reporte         = COALESCE(EXCLUDED.fecha_reporte,         censo_reporte.fecha_reporte),
    semana_epidemiologica = COALESCE(EXCLUDED.semana_epidemiologica, censo_reporte.semana_epidemiologica);

  -- =========================================
  -- ✅ RESPUESTA OK
  -- =========================================
  RETURN json_build_object('ok', true, 'id_paciente', p_id_paciente);

-- =========================================
-- ❌ MANEJO DE ERRORES
-- =========================================
EXCEPTION
  WHEN unique_violation THEN
    RETURN json_build_object('ok', false, 'error', 'Conflicto de datos únicos (CURP duplicado)');
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
-- FUNCION-TRIGGER NOTIFICACIONES
-- =========================================
-- Función compartida que inserta la notificación
CREATE OR REPLACE FUNCTION fn_insertar_notificacion()
RETURNS TRIGGER AS $$
DECLARE
  v_id_paciente INTEGER;
  v_mensaje     TEXT;
BEGIN

  -- ───────────────── CITA ─────────────────
  IF TG_TABLE_NAME = 'cita' THEN

    IF TG_OP = 'INSERT' THEN
      v_id_paciente := NEW.id_paciente;
      v_mensaje := 'Se ha agendado una nueva cita para el ' ||
                   to_char(NEW.fecha, 'DD/MM/YYYY') || ' a las ' ||
                   to_char(NEW.hora, 'HH12:MI AM') || '.';

    ELSIF TG_OP = 'UPDATE' THEN
      IF OLD.estado <> 'cancelada' AND NEW.estado = 'cancelada' THEN
        v_id_paciente := NEW.id_paciente;
        v_mensaje := 'Tu cita del ' || to_char(NEW.fecha, 'DD/MM/YYYY') ||
                     ' ha sido cancelada. Por favor contáctanos para reagendar.';
      ELSE
        RETURN NEW;
      END IF;
    END IF;

  -- ─────────────── INASISTENCIA ───────────────
  ELSIF TG_TABLE_NAME = 'inasistencia' THEN

    IF TG_OP = 'INSERT' THEN
      SELECT id_paciente INTO v_id_paciente
      FROM cita WHERE id_cita = NEW.id_cita;

      IF v_id_paciente IS NULL THEN
        RETURN NEW;
      END IF;

      v_mensaje := 'Registramos que no pudiste asistir a tu cita. ' ||
                   'Pronto nos pondremos en contacto contigo.';

    ELSIF TG_OP = 'UPDATE' THEN
      IF NEW.mensaje_seguimiento IS NOT NULL
         AND OLD.mensaje_seguimiento IS DISTINCT FROM NEW.mensaje_seguimiento THEN

        SELECT id_paciente INTO v_id_paciente
        FROM cita WHERE id_cita = NEW.id_cita;

        v_mensaje := NEW.mensaje_seguimiento;
      ELSE
        RETURN NEW;
      END IF;
    END IF;

  -- ─────────────── CONSULTA ───────────────
  ELSIF TG_TABLE_NAME = 'consulta' THEN

    IF TG_OP = 'INSERT' THEN
      v_id_paciente := NEW.id_paciente;
      v_mensaje := 'Se ha registrado tu consulta. Diagnóstico: ' ||
                   COALESCE(NEW.diagnostico, 'pendiente') || '.';
    END IF;

  -- ─────────────── CONTROL PRENATAL ───────────────
  ELSIF TG_TABLE_NAME = 'control_prenatal' THEN

    IF TG_OP = 'INSERT'
       OR OLD.semanas_gestacion IS DISTINCT FROM NEW.semanas_gestacion THEN

      v_id_paciente := NEW.id_paciente;
      v_mensaje := 'Tu control prenatal ha sido actualizado. ' ||
                   'Semanas de gestación: ' ||
                   COALESCE(NEW.semanas_gestacion::TEXT, 'sin registro') || '.';
    ELSE
      RETURN NEW;
    END IF;

  -- ─────────────── SINTOMA ───────────────
  ELSIF TG_TABLE_NAME = 'sintoma' THEN

    IF TG_OP = 'INSERT' THEN
      v_id_paciente := NEW.id_paciente;
      v_mensaje := 'Hemos recibido el reporte de tu síntoma: ' ||
                   NEW.descripcion || '. Un médico lo revisará pronto.';
    END IF;

  ELSE
    RETURN NEW;
  END IF;

  -- VALIDACIÓN GLOBAL
  IF v_id_paciente IS NULL THEN
    RETURN NEW;
  END IF;

  -- INSERT SEGURO
  BEGIN
    INSERT INTO notificacion (id_paciente, mensaje)
    VALUES (v_id_paciente, v_mensaje);

  EXCEPTION
    WHEN OTHERS THEN
      RAISE NOTICE 'Error insertando notificación: %', SQLERRM;
  END;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ── TRIGGERS ────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_notif_cita_nueva
  AFTER INSERT ON cita
  FOR EACH ROW EXECUTE FUNCTION fn_insertar_notificacion();

CREATE TRIGGER trg_notif_cita_cancelada
  AFTER UPDATE OF estado ON cita
  FOR EACH ROW EXECUTE FUNCTION fn_insertar_notificacion();

CREATE TRIGGER trg_notif_inasistencia
  AFTER INSERT ON inasistencia
  FOR EACH ROW EXECUTE FUNCTION fn_insertar_notificacion();

CREATE TRIGGER trg_notif_mensaje_seguimiento
  AFTER UPDATE OF mensaje_seguimiento ON inasistencia
  FOR EACH ROW EXECUTE FUNCTION fn_insertar_notificacion();

CREATE TRIGGER trg_notif_consulta
  AFTER INSERT ON consulta
  FOR EACH ROW EXECUTE FUNCTION fn_insertar_notificacion();

CREATE TRIGGER trg_notif_control_prenatal
  AFTER INSERT OR UPDATE ON control_prenatal
  FOR EACH ROW EXECUTE FUNCTION fn_insertar_notificacion();

CREATE TRIGGER trg_notif_sintoma
  AFTER INSERT ON sintoma
  FOR EACH ROW EXECUTE FUNCTION fn_insertar_notificacion();


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

-- =========================================
-- VISTA: CITAS
-- =========================================
CREATE OR REPLACE VIEW vista_cita AS
SELECT
    c.id_cita,
    c.fecha,
    c.hora,
    c.estado,
    c.area,

    p.id_paciente,
    p.nombre AS paciente,

    u.nombre AS medico

FROM cita c
JOIN paciente p ON p.id_paciente = c.id_paciente
LEFT JOIN usuario u ON u.id_usuario = c.id_usuario;

-- =========================================
-- VISTA: CITAS STATS
-- =========================================
CREATE OR REPLACE VIEW vista_dashboard_citas AS
SELECT
    -- Citas para hoy
    COUNT(*) FILTER (
        WHERE fecha = CURRENT_DATE
    ) AS citas_hoy,

    -- Citas esta semana
    COUNT(*) FILTER (
        WHERE fecha >= DATE_TRUNC('week', CURRENT_DATE)
        AND fecha < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '7 days'
    ) AS citas_semana,

    -- Pendientes
    COUNT(*) FILTER (
        WHERE estado = 'pendiente'
    ) AS pendientes,

    -- Inasistencias del mes
    COUNT(*) FILTER (
        WHERE estado = 'inasistencia'
        AND DATE_TRUNC('month', fecha) = DATE_TRUNC('month', CURRENT_DATE)
    ) AS inasistencias_mes

FROM cita;

-- =========================================
-- VISTA: INASISTENCIAS
-- =========================================
CREATE OR REPLACE VIEW vista_inasistencias_detalle AS
SELECT
    -- Datos del paciente
    p.id_paciente,
    p.nombre                          AS nombre_paciente,
    p.semanas_gestacion               AS sdg,

    -- Datos de la cita
    c.id_cita,
    c.fecha                           AS fecha_cita,
    c.hora                            AS hora_cita,
    c.estado                          AS estado_cita,
    c.area,

    -- Datos de inasistencia
    i.id_inasistencia,
    i.motivo                          AS motivo_inasistencia,
    i.justificada,
    i.fecha                           AS fecha_inasistencia,
    i.mensaje_seguimiento,
    i.observacion_ts                  AS observacion_inasistencia,

    -- Usuario que registró la cita (trabajador social)
    u.nombre                          AS nombre_usuario,
    u.rol                             AS rol_usuario

FROM inasistencia i
JOIN cita c          ON c.id_cita     = i.id_cita
JOIN paciente p      ON p.id_paciente = c.id_paciente
LEFT JOIN usuario u  ON u.id_usuario  = c.id_usuario
WHERE c.estado = 'inasistencia';

-- =========================================
-- VISTA: CENSO TABLA
-- =========================================
CREATE OR REPLACE VIEW vista_censo_tabla AS
SELECT
    -- Número consecutivo
    us.no_consecutivo AS numero,

    -- Datos del paciente
    p.id_paciente,
    p.nombre AS nombre_completo,
    p.curp,
    p.edad,
    COALESCE(p.municipio, us.municipio) AS municipio,

    -- Control prenatal
    cp.semanas_gestacion AS sdg,
    cp.fpp,
    cp.riesgo_obstetrico AS riesgo,
    cp.consultas_otorgadas AS consultas

FROM paciente p

LEFT JOIN unidad_salud us 
    ON p.id_paciente = us.id_paciente

LEFT JOIN control_prenatal cp 
    ON p.id_paciente = cp.id_paciente;

-- =========================================
-- VISTA: DETALLE CENSO PACIENTE
-- =========================================
CREATE OR REPLACE VIEW vista_reporte_cpn AS
SELECT
    -- ───────── 1. ENCABEZADO ─────────
    cr.id_censo,
    cr.mes_reporte,
    cr.fecha_reporte,
    cr.semana_epidemiologica,

    -- ───────── 2. ZONA DE ATENCIÓN ─────────
    us.region,
    us.no_consecutivo,
    cp.fecha_ingreso_cpn,
    us.clues_imb,
    us.municipio AS municipio,
    us.tipo_localidad,
    us.nombre_unidad,
    us.zona_servicios,

    -- ───────── 3. DATOS PACIENTE ─────────
    p.id_paciente,
    p.nombre,
    p.curp,
    p.edad,
    p.lengua_indigena,
    p.colonia,

    -- ───────── 4. ANTECEDENTES ─────────
    cp.fur,
    cp.fpp,
    cp.semanas_gestacion,
    cp.gestas,
    cp.partos,
    cp.cesareas,
    cp.abortos,

    -- ───────── 5. SEGUIMIENTO ─────────
    cp.consultas_otorgadas,
    cp.factores_riesgo,
    cp.riesgo_social,
    cp.estado_salud,
    cp.riesgo_obstetrico,
    cp.fecha_ultima_atencion,

    -- ───────── 6. CONSULTA (ÚLTIMA) ─────────
    con.diagnostico,
    con.tratamiento,

    -- ───────── 7. INASISTENCIA (SI EXISTE) ─────────
    i.motivo,
    i.observacion_ts,
    i.mensaje_seguimiento,

    -- ───────── CAMPOS PLACEHOLDER ─────────
    NULL::text AS control_prenatal_inicio,
    NULL::text AS vacunas,
    NULL::text AS detecciones,
    NULL::text AS puerperio,
    NULL::text AS plan_accion,

    -- 🔥 AQUÍ VA EL RESPONSABLE REAL
    u.nombre AS responsable,

    NULL::text AS observaciones

FROM paciente p

-- RELACIONES
LEFT JOIN censo_reporte cr 
    ON p.id_paciente = cr.id_paciente

LEFT JOIN unidad_salud us 
    ON p.id_paciente = us.id_paciente

-- CONTROL PRENATAL
LEFT JOIN LATERAL (
    SELECT *
    FROM control_prenatal cp
    WHERE cp.id_paciente = p.id_paciente
    LIMIT 1
) cp ON TRUE

-- ÚLTIMA CONSULTA
LEFT JOIN LATERAL (
    SELECT *
    FROM consulta c
    WHERE c.id_paciente = p.id_paciente
    ORDER BY c.fecha DESC
    LIMIT 1
) con ON TRUE

-- 🔥 ÚLTIMA CITA (PARA OBTENER DOCTOR)
LEFT JOIN LATERAL (
    SELECT *
    FROM cita ct
    WHERE ct.id_paciente = p.id_paciente
    ORDER BY ct.fecha DESC, ct.hora DESC
    LIMIT 1
) ct ON TRUE

-- 🔥 USUARIO (DOCTOR)
LEFT JOIN usuario u 
    ON u.id_usuario = ct.id_usuario

-- ÚLTIMA INASISTENCIA
LEFT JOIN LATERAL (
    SELECT i.*
    FROM inasistencia i
    JOIN cita cti ON cti.id_cita = i.id_cita
    WHERE cti.id_paciente = p.id_paciente
    ORDER BY i.fecha DESC
    LIMIT 1
) i ON TRUE;

-- ========================================='
-- FUNCION: ACTUALIZAR CENSO
-- =========================================
CREATE OR REPLACE FUNCTION fn_actualizar_reporte_cpn(
    -- IDENTIFICADOR
    p_id_paciente INT,

    -- PACIENTE
    p_nombre TEXT,
    p_edad INT,
    p_curp TEXT,
    p_colonia TEXT,
    p_lengua_indigena TEXT,

    -- UNIDAD SALUD
    p_region TEXT,
    p_municipio TEXT,
    p_tipo_localidad TEXT,
    p_nombre_unidad TEXT,
    p_zona_servicios TEXT,

    -- CONTROL PRENATAL
    p_semanas_gestacion INT,
    p_gestas INT,
    p_partos INT,
    p_cesareas INT,
    p_abortos INT,
    p_riesgo_obstetrico TEXT,
    p_estado_salud TEXT,
    p_consultas_otorgadas INT,
    p_factores_riesgo TEXT,

    -- CENSO
    p_mes_reporte TEXT,
    p_fecha_reporte DATE,
    p_semana_epidemiologica INT
)
RETURNS void AS $$
BEGIN

    -- 🟢 PACIENTE
    UPDATE paciente
    SET nombre = p_nombre,
        edad = p_edad,
        curp = p_curp,
        colonia = p_colonia,
        lengua_indigena = p_lengua_indigena
    WHERE id_paciente = p_id_paciente;

    -- 🟢 UNIDAD SALUD
    UPDATE unidad_salud
    SET region = p_region,
        municipio = p_municipio,
        tipo_localidad = p_tipo_localidad,
        nombre_unidad = p_nombre_unidad,
        zona_servicios = p_zona_servicios
    WHERE id_paciente = p_id_paciente;

    -- 🟢 CONTROL PRENATAL
    UPDATE control_prenatal
    SET semanas_gestacion = p_semanas_gestacion,
        gestas = p_gestas,
        partos = p_partos,
        cesareas = p_cesareas,
        abortos = p_abortos,
        riesgo_obstetrico = p_riesgo_obstetrico,
        estado_salud = p_estado_salud,
        consultas_otorgadas = p_consultas_otorgadas,
        factores_riesgo = p_factores_riesgo
    WHERE id_paciente = p_id_paciente;

    -- 🟢 CENSO
    UPDATE censo_reporte
    SET mes_reporte = p_mes_reporte,
        fecha_reporte = p_fecha_reporte,
        semana_epidemiologica = p_semana_epidemiologica
    WHERE id_paciente = p_id_paciente;

END;
$$ LANGUAGE plpgsql;