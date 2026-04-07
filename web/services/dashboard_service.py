from utils.supabase_client import supabase

def get_dashboard_stats():
    try:
        response = supabase.table("dashboard_stats").select("*").execute()
        
        return {
            "data": response.data[0],
            "message": "success",
            "error": None
        }

    except Exception as e:
        return {
            "data": {},
            "message": "fail",
            "error": str(e)
        }
def get_actividad_reciente():
    try:
        response = supabase.table("actividad_reciente").select("*").execute()
        
        return {
            "data": response.data,
            "message": "success",
            "error": None
        }

    except Exception as e:
        return {
            "data": {},
            "message": "fail",
            "error": str(e)
        }

def get_estadistica_dashboard():
    try:
        response = supabase.table("estadisticas_dashboard").select("*").execute()
        

        return {
            "data": response.data[0],
            "message": "success",
            "error": None
        }

    except Exception as e:
        return {
            "data": {},
            "message": "fail",
            "error": str(e)
        }

