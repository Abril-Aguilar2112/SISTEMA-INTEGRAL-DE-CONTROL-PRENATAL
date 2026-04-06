from pydantic import BaseModel
from typing import Optional

class Paciente(BaseModel):
    id_paciente: int
    id_usuario: Optional[int]
    nombre: str
    edad: Optional[int]
    telefono: Optional[str]
    semanas_gestacion: Optional[int]
    nivel_riesgo: Optional[str]