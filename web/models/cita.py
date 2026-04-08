from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional

class Cita(BaseModel):
    id_cita: int
    id_paciente: Optional[int]
    fecha: date
    hora: str
    estado: Optional[str]

class CitaUpdate(BaseModel):
    fecha: Optional[date] = None
    hora: Optional[str] = None
    estado: Optional[str] = None
    id_usuario: Optional[int] = None
    area: Optional[str] = None

    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    @field_validator('hora', mode='before')
    @classmethod
    def convert_time(cls, v):
        if v and 'AM' in v or 'PM' in v:
            try:
                # Convierte "10:00 AM" a "10:00:00"
                in_time = datetime.strptime(v, "%I:%M %p")
                return in_time.strftime("%H:%M:%S")
            except:
                return v
        return v

class CitaReagendar(BaseModel):
    fecha: date
    hora: str

class CitaCreate(BaseModel):
    id_paciente: int
    fecha: date
    hora: str
    id_usuario: int
    area: str
    observaciones: Optional[str] = None

    @field_validator('hora', mode='before')
    @classmethod
    def convert_time(cls, v):
        if not v:
            return v
        
        # Si ya viene con AM/PM (formato antiguo o de otros formularios)
        if 'AM' in v or 'PM' in v:
            try:
                in_time = datetime.strptime(v, "%I:%M %p")
                return in_time.strftime("%H:%M:00")
            except:
                return v
        
        # Si viene como HH:MM
        if len(v) == 5 and ':' in v:
            return f"{v}:00"
            
        return v
   