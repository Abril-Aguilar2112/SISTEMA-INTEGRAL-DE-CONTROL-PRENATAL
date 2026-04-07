from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date

class Paciente(BaseModel):
    id_paciente: int
    id_usuario: Optional[int]
    nombre: str
    edad: Optional[int]
    telefono: Optional[str]
    semanas_gestacion: Optional[int]
    nivel_riesgo: Optional[str]


class PacienteCreate(BaseModel):
    # — Datos de usuario —
    id_usuario: int 
 
    # — Datos personales —
    nombre:           str
    edad:             int            = Field(gt=0, lt=60)
    telefono:         Optional[str]  = None
    curp:             Optional[str]  = None
    colonia:          Optional[str]  = None
    lengua_indigena:  Optional[str]  = None
 
    # — Control prenatal —
    semanas_gestacion:    int            = Field(ge=0, le=42)
    fur:                  Optional[date] = None
    fpp:                  Optional[date] = None
    riesgo_obstetrico:    Optional[str]  = None
    riesgo_social:        Optional[str]  = None
    factores_riesgo:      Optional[str]  = None
    consultas_otorgadas:  Optional[int]  = 0
    estado_salud:         Optional[str]  = None
 
    # — Antecedentes obstétricos —
    gestas:                 Optional[int]  = 0
    partos:                 Optional[int]  = 0
    cesareas:               Optional[int]  = 0
    abortos:                Optional[int]  = 0
    fecha_ultima_atencion:  Optional[date] = None
    fecha_ingreso_cpn:      Optional[date] = None
 
    # — Historial clínico —
    antecedentes:   Optional[str] = None
    observaciones:  Optional[str] = None
 
    # — Unidad de salud —
    region:          Optional[str] = None
    clues_imb:       Optional[str] = None
    municipio:       Optional[str] = None
    tipo_localidad:  Optional[str] = None
    nombre_unidad:   Optional[str] = None
    zona_servicios:  Optional[str] = None
    no_consecutivo:  Optional[str] = None

    # — Censo / reporte —
    mes_reporte:           Optional[str]  = None
    fecha_reporte:         Optional[date] = None
    semana_epidemiologica: Optional[int]  = None

    # Validador para convertir "" en None (Crucial para formularios HTML)
    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v
 
    def to_rpc(self) -> dict:
        def d(v):
            return v.isoformat() if isinstance(v, date) else v

        return {
            "id_usuario": self.id_usuario,
            # Datos personales
            "p_nombre": self.nombre,
            "p_edad": self.edad,
            "p_telefono": self.telefono,
            "p_curp": getattr(self, "curp", None),
            "p_colonia": getattr(self, "colonia", None),
            "p_lengua_indigena": getattr(self, "lengua_indigena", None),

            # Control prenatal
            "p_semanas": self.semanas_gestacion,
            "p_fur": d(self.fur),
            "p_fpp": d(self.fpp),
            "p_riesgo_obstetrico": self.riesgo_obstetrico,
            "p_riesgo_social": self.riesgo_social,
            "p_factores": self.factores_riesgo,
            "p_consultas": self.consultas_otorgadas,
            "p_estado_salud": self.estado_salud,

            # Antecedentes obstétricos
            "p_gestas": self.gestas,
            "p_partos": self.partos,
            "p_cesareas": self.cesareas,
            "p_abortos": self.abortos,
            "p_fecha_ultima_atencion": d(getattr(self, "fecha_ultima_atencion", None)),
            "p_fecha_ingreso_cpn": d(getattr(self, "fecha_ingreso_cpn", None)),

            # Historial clínico
            "p_antecedentes": self.antecedentes,
            "p_observaciones": self.observaciones,

            # Unidad de salud
            "p_region": getattr(self, "region", None),
            "p_clues_imb": getattr(self, "clues_imb", None),
            "p_municipio": getattr(self, "municipio", None),
            "p_tipo_localidad": getattr(self, "tipo_localidad", None),
            "p_nombre_unidad": getattr(self, "nombre_unidad", None),
            "p_zona_servicios": getattr(self, "zona_servicios", None),
            "p_no_consecutivo": getattr(self, "no_consecutivo", None),

            # Censo / reporte
            "p_mes_reporte": getattr(self, "mes_reporte", None),
            "p_fecha_reporte": d(getattr(self, "fecha_reporte", None)),
            "p_semana_epidemiologica": getattr(self, "semana_epidemiologica", None),
        }

class PacienteUpdate(BaseModel):
    id_paciente: int

    # Datos personales
    nombre: Optional[str] = None
    edad: Optional[int] = Field(default=None, gt=0)
    telefono: Optional[str] = None
    curp: Optional[str] = None
    colonia: Optional[str] = None
    lengua_indigena: Optional[str] = None

    # Control prenatal
    fur: Optional[date] = None
    fpp: Optional[date] = None
    semanas_gestacion: Optional[int] = Field(default=None, ge=0, le=42)
    fecha_ingreso_cpn: Optional[date] = None
    fecha_ultima_atencion: Optional[date] = None
    gestas: Optional[int] = None
    partos: Optional[int] = None
    cesareas: Optional[int] = None
    abortos: Optional[int] = None
    riesgo_obstetrico: Optional[str] = None
    riesgo_social: Optional[str] = None
    factores_riesgo: Optional[str] = None
    consultas_otorgadas: Optional[int] = None
    estado_salud: Optional[str] = None

    # Unidad de salud
    region: Optional[str] = None
    clues_imb: Optional[str] = None
    municipio: Optional[str] = None
    tipo_localidad: Optional[str] = None
    nombre_unidad: Optional[str] = None
    zona_servicios: Optional[str] = None
    no_consecutivo: Optional[str] = None

    # Censo
    mes_reporte: Optional[str] = None
    fecha_reporte: Optional[date] = None
    semana_epidemiologica: Optional[int] = None

    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        return None if v == "" else v

    def to_rpc(self):
        return {
            "p_id_paciente": self.id_paciente,

            "p_nombre": self.nombre,
            "p_edad": self.edad,
            "p_telefono": self.telefono,
            "p_curp": self.curp,
            "p_colonia": self.colonia,
            "p_lengua_indigena": self.lengua_indigena,

            "p_semanas": self.semanas_gestacion,
            "p_fur": self.fur.isoformat() if self.fur else None,
            "p_fpp": self.fpp.isoformat() if self.fpp else None,
            "p_fecha_ingreso_cpn": self.fecha_ingreso_cpn.isoformat() if self.fecha_ingreso_cpn else None,
            "p_fecha_ultima_atencion": self.fecha_ultima_atencion.isoformat() if self.fecha_ultima_atencion else None,

            "p_gestas": self.gestas,
            "p_partos": self.partos,
            "p_cesareas": self.cesareas,
            "p_abortos": self.abortos,

            "p_riesgo_obstetrico": self.riesgo_obstetrico,
            "p_riesgo_social": self.riesgo_social,

            "p_factores": self.factores_riesgo,
            "p_consultas": self.consultas_otorgadas,

            "p_estado_salud": self.estado_salud,

            "p_region": self.region,
            "p_clues_imb": self.clues_imb,
            "p_municipio": self.municipio,
            "p_tipo_localidad": self.tipo_localidad,
            "p_nombre_unidad": self.nombre_unidad,
            "p_zona_servicios": self.zona_servicios,
            "p_no_consecutivo": self.no_consecutivo,

            # Censo
            "p_mes_reporte": self.mes_reporte,
            "p_fecha_reporte": self.fecha_reporte.isoformat() if self.fecha_reporte else None,
            "p_semana_epidemiologica": self.semana_epidemiologica
        }