from pydantic import BaseModel
from typing import Optional

class HistorialClinico(BaseModel):
    id_historial: int
    id_paciente: int
    antecedentes: Optional[str]
    observaciones: Optional[str]