from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class Cita(BaseModel):
    id_cita: int
    id_paciente: Optional[int]
    fecha: date
    hora: time
    estado: Optional[str]