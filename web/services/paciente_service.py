from utils.supabase_client import supabase

def get_pacientes(page=1, search='', riesgo='', semanas=''):
    try:
        per_page = 10
        offset = (page - 1) * per_page

        query = supabase.table("pacientes_dashboard").select("*", count="exact")

        if search:
            query = query.ilike("nombre", f"%{search}%")

        if riesgo:
            query = query.eq("nivel_riesgo", riesgo)

        if semanas:
            rangos = {
                "1-12": (1, 12),
                "13-24": (13, 24),
                "25-36": (25, 36),
                "37+": (37, None)
            }

            min_s, max_s = rangos.get(semanas, (None, None))

            if min_s is not None:
                query = query.gte("semanas_gestacion", min_s)

            if max_s is not None:
                query = query.lte("semanas_gestacion", max_s)

        query = query.not_.is_("semanas_gestacion", None)

        response = query.range(offset, offset + per_page - 1).execute()

        total = response.count or 0
        total_pages = (total // per_page) + (1 if total % per_page else 0)

        return {
            "data": response.data or [],
            "page": page,
            "total_pages": total_pages,
            "total_records": total,
            "page_size": per_page,
            "error": None
        }

    except Exception as e:
        return {
            "data": [],
            "page": 1,
            "total_pages": 0,
            "total_records": 0,
            "page_size": 10,
            "error": str(e)
        }

def crear_paciente(data):
    try:
        return supabase.table("paciente").insert({
            "nombre": data["nombre"],
            "edad": data["edad"],
            "telefono": data.get("telefono"),
            "semanas_gestacion": data.get("semanas_gestacion")
        }).execute()
    except Exception as e:
        return {"error": str(e)}

def registrar_paciente(data):
    res = supabase.rpc(
        "registrar_paciente_completo",
        data
    ).execute()

    return res.data

def actualizar_paciente(data):
    res = supabase.rpc(
        "actualizar_paciente",
        data
    ).execute()

    return res.data

def get_paciente_by_id(id_paciente: int):
    try:
        # Traemos los datos de todas las tablas relacionadas
        p = supabase.table("paciente").select("*").eq("id_paciente", id_paciente).single().execute()
        cp = supabase.table("control_prenatal").select("*").eq("id_paciente", id_paciente).single().execute()
        us = supabase.table("unidad_salud").select("*").eq("id_paciente", id_paciente).single().execute()
        cr = supabase.table("censo_reporte").select("*").eq("id_paciente", id_paciente).single().execute()
        
        # Combinamos todo en un solo diccionario para el formulario
        paciente_data = {**p.data}
        
        if cp.data:
            paciente_data.update(cp.data)
        if us.data:
            paciente_data.update(us.data)
        if cr.data:
            paciente_data.update(cr.data)
            
        return {"data": paciente_data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}
