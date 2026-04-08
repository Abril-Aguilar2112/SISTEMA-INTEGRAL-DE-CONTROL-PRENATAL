from httpx import Response
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

def get_inasistencias(search='', estatus='', fecha=''):
    try:
        query = supabase.from_("vista_inasistencias_detalle").select("*", count="exact")

        if search:
            if search.isdigit():
                query = query.or_(f"id_paciente.eq.{search},nombre_paciente.ilike.%{search}%")
            else:
                query = query.ilike("nombre_paciente", f"%{search}%") 

        if estatus:
            query = query.eq("estatus", estatus)

        if fecha:
            query = query.eq("fecha", fecha)

        response = query.execute()

        return {
            "data": response.data or [],
            "count": response.count or 0,
            "message": "success" if response.data else "empty",
            "error": None
        }

    except Exception as e:
        return {
            "data": [],
            "count": 0,
            "message": "error",
            "error": str(e)
        }

def actualizar_inasistencia(data: dict, id_inasistencia: str):
    try:
        response = supabase.table("inasistencia").update(data).eq("id_inasistencia", id_inasistencia).execute()
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
