from utils.supabase_client import supabase

def get_citas():
    try:
        response = supabase.from_("vista_citas").select().execute()

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

def get_cita_by_id(id_cita: int):
    try:
        response = supabase.rpc("get_cita_by_id", {"p_id": id_cita}).execute()

        return {
            "data": response.data["data"],
            "message": "success",
            "error": None
        }

    except Exception as e:
        return {
            "data": {},
            "message": "error",
            "error": str(e)
        }

def update_cita(cita: dict, id_cita: int):
    try:
        response = supabase.table("cita").update(cita).eq("id_cita", id_cita).execute()

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
