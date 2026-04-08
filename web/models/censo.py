from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date

class CensoReporteUpdate(BaseModel):
    # IDENTIFICADOR
    id_paciente: int

    # PACIENTE
    nombre: str
    edad: int
    curp: Optional[str] = None
    colonia: Optional[str] = None
    lengua_indigena: Optional[str] = None

    # UNIDAD SALUD
    region: Optional[str] = None
    municipio: Optional[str] = None
    tipo_localidad: Optional[str] = None
    nombre_unidad: Optional[str] = None
    zona_servicios: Optional[str] = None

    # CONTROL PRENATAL
    semanas_gestacion: int
    gestas: int
    partos: int
    cesareas: int
    abortos: int
    riesgo_obstetrico: Optional[str] = None
    estado_salud: Optional[str] = None
    consultas_otorgadas: int
    factores_riesgo: Optional[str] = None

    # CENSO
    mes_reporte: Optional[str] = None
    fecha_reporte: Optional[date] = None
    semana_epidemiologica: Optional[int] = None

    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    def to_rpc(self) -> dict:
        def format_date(v):
            return v.isoformat() if isinstance(v, date) else v

        return {
            "p_id_paciente": self.id_paciente,
            "p_nombre": self.nombre,
            "p_edad": self.edad,
            "p_curp": self.curp,
            "p_colonia": self.colonia,
            "p_lengua_indigena": self.lengua_indigena,
            "p_region": self.region,
            "p_municipio": self.municipio,
            "p_tipo_localidad": self.tipo_localidad,
            "p_nombre_unidad": self.nombre_unidad,
            "p_zona_servicios": self.zona_servicios,
            "p_semanas_gestacion": self.semanas_gestacion,
            "p_gestas": self.gestas,
            "p_partos": self.partos,
            "p_cesareas": self.cesareas,
            "p_abortos": self.abortos,
            "p_riesgo_obstetrico": self.riesgo_obstetrico,
            "p_estado_salud": self.estado_salud,
            "p_consultas_otorgadas": self.consultas_otorgadas,
            "p_factores_riesgo": self.factores_riesgo,
            "p_mes_reporte": self.mes_reporte,
            "p_fecha_reporte": format_date(self.fecha_reporte),
            "p_semana_epidemiologica": self.semana_epidemiologica
        }
