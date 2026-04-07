from utils.supabase_client import supabase

def get_pacientes(page=1, limit=5, riesgo=None, search=None):
    try:
        query = supabase.table("pacientes_dashboard").select("*", count="exact")

        if riesgo and riesgo != "Todos":
            query = query.eq("nivel_riesgo", riesgo.lower())

        if search:
            query = query.ilike("nombre", f"%{search}%")

        start = (page - 1) * limit
        end = start + limit - 1

        response = query.range(start, end).execute()

        return {
            "data": response.data,
            "count": response.count,
            "page": page,
            "total_pages": (response.count // limit) + 1,
            "error": None
        }

    except Exception as e:
        return {
            "data": [],
            "count": 0,
            "page": page,
            "total_pages": 0,
            "error": str(e)
        }