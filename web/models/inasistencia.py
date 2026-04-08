from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InasistenciaCreate(BaseModel):
    id_cita: Optional[int] = None
    motivo: Optional[str] = None
    justificada: Optional[bool] = None
    fecha: Optional[datetime] = None

