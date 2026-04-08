from utils.supabase_client import supabase

def get_censo_tabla():
    try:
        response = supabase.from_("vista_censo_tabla").select("*").execute()
        if response.data is not None:
            return {
                "data": response.data,
                "message": "success",
                "error": None
            }
        else:
            return {
                "data": [],
                "message": "success",
                "error": None
            }
    except Exception as e:
        return {
            "data": None,
            "message": "error",
            "error": str(e)
        }

def get_censo_reporte(id_paciente):
    try:
        response = supabase.from_("vista_reporte_cpn").select("*").eq("id_paciente", id_paciente).execute()
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
                "error": "No se encontró datos"
            }
    except Exception as e:
        return {
            "data": None,
            "message": "error",
            "error": str(e)
        }

def actualizar_censo(id_paciente: int, data: dict):
    try:
        if "p_id_paciente" not in data:
            data["p_id_paciente"] = id_paciente
            
        response = supabase.rpc("fn_actualizar_reporte_cpn", data).execute()
        
        return {
            "data": response.data[0] if (response.data and len(response.data) > 0) else response.data,
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": None,
            "message": "error",
            "error": str(e)
        }
   
