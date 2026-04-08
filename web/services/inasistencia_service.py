from utils.supabase_client import supabase 

def crear_inasistencia(data: dict):
    try:
        response = supabase.table("inasistencia").insert(data).execute()
        if response.data:
            return {
                "data": response.data,
                "message": "success",
                "error": None
            }
    except Exception as e:
        return {
            "data": {},
            "message": "error",
            "error": str(e)
        }

