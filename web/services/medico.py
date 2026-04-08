from utils.supabase_client import supabase

def get_medicos():
    try:
        response = supabase.from_("usuario").select("id_usuario", "nombre").eq("rol", "medico").execute()
        return {
            "data": response.data,
            "message": "success",
            "error": None
        }

    except Exception as e:
        return {
            "data": [],
            "message": "error",
            "error": str(e)
        }