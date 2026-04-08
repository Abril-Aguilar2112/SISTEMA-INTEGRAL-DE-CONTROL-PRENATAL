from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ObservacionInasistenciaEnum(str, Enum):
    NUEVA_CITA = 'Se le agendará nueva cita'
    CANALIZAR_TRABAJO_SOCIAL = 'Se canalizará a trabajo social'
    BAJA_TEMPORAL = 'Se dará de baja temporalmente'
    SIN_ACCION_REQUERIDA = 'Sin acción requerida'

class InasistenciaCreate(BaseModel):
    id_cita: Optional[int] = None
    motivo: Optional[str] = None
    justificada: Optional[bool] = None
    fecha: Optional[datetime] = None

class InasistenciaContestar(BaseModel):
    observacion_ts: Optional[ObservacionInasistenciaEnum]
    mensaje_seguimiento: Optional[str] = None

