from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Dict, Any, List

class ReporteBase(BaseModel):
    id_usuario: Optional[int] = None
    periodo_inicio: date
    periodo_fin: date
    generado_por: str
    tipo: str
    datos: Dict[str, Any]

class ReporteCreate(ReporteBase):
    estado: str

class ReporteUpdate(BaseModel):
    estado: Optional[str] = None
    datos: Optional[Dict[str, Any]] = None

class ReporteResponse(ReporteBase):
    id_reporte: int
    fecha: date
    datos: Dict[str, Any]

    class Config:
        from_attributes = True
