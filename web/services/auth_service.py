from utils.supabase_client import supabase
from models.auth import LoginRequest

def register_user(data):
    try:
        existing = supabase.table("usuario").select().eq("correo", data.correo).execute()

        if existing.data:
            return {"data": {}, "message": "Ocurrio un error", "error": "El correo ya está registrado"}

        auth_response = supabase.auth.sign_up({
            "email": data.correo,
            "password": data.password
        })

        if auth_response.user is None:
            return {"data": {}, "message": "Ocurrio un error", "error": "No se pudo registrar"}

        
        user_data = {
            "auth_id": auth_response.user.id,
            "correo": data.correo,
            "nombre": data.nombre,
            "rol": data.rol
        }

        db_response = supabase.table("usuario").insert(user_data).execute()

        if not db_response.data:
            return {"data": {}, "message": "Ocurrio un error", "error": "No se pudo registrar el usuario"}

        usuario_db = db_response.data

        return {
            "data": {
                "id_usuario": usuario_db["id_usuario"],
                "nombre": usuario_db["nombre"],
                "correo": usuario_db["correo"],
                "rol": usuario_db["rol"],
                "access_token": auth_response.session.access_token
            },
            "message": "Usuario registrado exitosamente",
            "error": None
        }

    except Exception as e:
        return {"data": {}, "message": "Ocurrio un error", "error": str(e)}


def login_user(data: LoginRequest):
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": data.correo,
            "password": data.password
        })

        if not auth_response.user:
            return {"data": {}, "message": "Ocurrio un error", "error": "Credenciales inválidas"}

        user = auth_response.user

        db_response = supabase.table("usuario").select().eq("auth_id", user.id).single().execute()

        if not db_response.data:
            return {"data": {}, "message": "Ocurrio un error", "error": "Usuario no registrado en el sistema"}

        if not db_response:
            return {"data": {}, "message": "Ocurrio un error", "error": "No se encontró el usuario"}

        usuario_db = db_response.data

        return {
            "data": {
                "id_usuario": usuario_db["id_usuario"],
                "nombre": usuario_db["nombre"],
                "correo": usuario_db["correo"],
                "rol": usuario_db["rol"],
                "access_token": auth_response.session.access_token
            },
            "message": "Inicio de sesión exitoso",
            "error": None
        }
    except Exception as e:
        return {"data": {}, "message": "Ocurrio un error", "error": str(e)}
