from utils.supabase_client import supabase

def get_stats_citas():
    try:
        response = supabase.from_("vista_dashboard_citas").select().execute()

        if response.data:
            return {
                "data": response.data[0],
                "message": "success",
                "error": None
            }

    except Exception as e:
        return {
            "data": {},
            "message": "error",
            "error": str(e)
        }
def get_citas(search='', fecha='', estado='', id_medico=None):
    try:
        query = supabase.from_("vista_citas").select("*", count="exact")
        if id_medico:
            query = query.eq("id_medico", id_medico)

        if search:
            if search.isdigit():
                query = query.or_(
                    f"id_paciente.eq.{search},paciente.ilike.%{search}%"
                )
            else:
                query = query.ilike("paciente", f"%{search}%")

        if fecha:
            query = query.eq("fecha", fecha)

        if estado:
            query = query.eq("estado", estado)

        
        response = query.execute()


        if response.data:
            return {
                "data": response.data, 
                "count": response.count,
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

def reagendar_cita(cita: dict, id_cita: int):
    try:
        response = supabase.table("cita").update(cita).eq("id_cita", id_cita).execute()
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

def set_estado_cita(id_cita: int, estado: str):
    try:
        response = supabase.table("cita").update({"estado": estado}).eq("id_cita", id_cita).execute()

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

def crear_cita(cita: dict):
    try:
        response = supabase.table("cita").insert(cita).execute()
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

def upsert_inasistencia(id_cita: int, motivo: str, justificada: bool = True):
    try:
        existing = supabase.table("inasistencia").select("id_inasistencia").eq("id_cita", id_cita).limit(1).execute()
        if existing.data:
            inasistencia_id = existing.data[0].get("id_inasistencia")
            response = supabase.table("inasistencia").update({"motivo": motivo, "justificada": justificada}).eq("id_inasistencia", inasistencia_id).execute()
        else:
            response = supabase.table("inasistencia").insert({"id_cita": id_cita, "motivo": motivo, "justificada": justificada}).execute()

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
