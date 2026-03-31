from app.web.utils.supabase_client import supabase

def register_user(email, password, nombre, rol):
    auth_response = supabase.auth.sign_up({
        "email": email,
        "password": password
    })

    if auth_response.user is None:
        return {"error": "No se pudo registrar"}

    user_data = {
        "auth_id": auth_response.user.id,
        "correo": email,
        "nombre": nombre,
        "rol": rol
    }

    supabase.table("usuario").insert(user_data).execute()

    return {"message": "Usuario registrado"}


def login_user(email, password):
    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if response.user is None:
        return {"error": "Credenciales inválidas"}

    return {
        "access_token": response.session.access_token,
        "user": response.user
    }