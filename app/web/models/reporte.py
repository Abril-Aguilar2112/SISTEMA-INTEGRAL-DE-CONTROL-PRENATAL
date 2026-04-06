from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class Reporte(BaseModel):
    id_reporte: int
    id_usuario: Optional[int]
    fecha: Optional[datetime]
    tipo: Optional[str]
    datos: Optional[Dict[str, Any]]