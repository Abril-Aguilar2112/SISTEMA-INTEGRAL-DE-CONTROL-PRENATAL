from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Consulta(BaseModel):
    id_consulta: int
    id_paciente: Optional[int]
    id_usuario: Optional[int]
    fecha: Optional[datetime]
    diagnostico: Optional[str]
    tratamiento: Optional[str]