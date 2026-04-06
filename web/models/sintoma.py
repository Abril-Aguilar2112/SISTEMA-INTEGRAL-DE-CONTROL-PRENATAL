from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Sintoma(BaseModel):
    id_sintoma: int
    id_paciente: Optional[int]
    descripcion: Optional[str]
    intensidad: Optional[str]
    fecha: Optional[datetime]