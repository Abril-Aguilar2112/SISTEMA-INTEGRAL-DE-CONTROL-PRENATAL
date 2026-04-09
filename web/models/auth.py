from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str

class UserRegistration(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    rol: str
