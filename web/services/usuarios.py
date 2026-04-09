from utils.supabase_client import supabase

def get_usuarios(search=None, rol=None, estado=None):
    try:
        query = supabase.table('usuario').select("*").neq('rol', 'director_general')
        
        if search:
            # Búsqueda en nombre o correo
            query = query.or_(f"nombre.ilike.%{search}%,correo.ilike.%{search}%")
        
        if rol:
            query = query.eq('rol', rol)
            
        if estado is not None:
            # estado viene como string o bool dependiendo de cómo se pase
            query = query.eq('estado', estado)
            
        response = query.execute()
        return {
            "data": response.data,
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": None,
            "message": "error",
            "error": str(e)
        }

def get_usuario_by_id(id_usuario):
    try:
        response = supabase.table('usuario').select("*").eq('id_usuario', id_usuario).execute()
        return {
            "data": response.data[0] if response.data else None,
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": None,
            "message": "error",
            "error": str(e)
        }

def create_usuario(data: dict):
    try:
        response = supabase.table("usuario").insert(data).execute()
        if response.data:
            return {
                "data": response.data[0],
                "message": "success",
                "error": None
            }
        else:
            return {
                "data": None,
                "message": "error",
                "error": "No se pudo crear el usuario"
            }
    except Exception as e:
        return {
            "data": None,
            "message": "error",
            "error": str(e)
        }

def update_usuario(id_usuario, data):
    try:
        response = supabase.table('usuario').update(data).eq('id_usuario', id_usuario).execute()
        return {
            "data": response.data[0] if response.data else None,
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": None,
            "message": "error",
            "error": str(e)
        }