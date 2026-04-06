from pydantic import BaseModel, EmailStr

class Usuario(BaseModel):
    id_usuario: int
    nombre: str
    correo: EmailStr
    rol: str