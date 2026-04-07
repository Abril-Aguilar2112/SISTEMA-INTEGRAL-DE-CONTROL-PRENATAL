from utils.supabase_client import supabase

def crear_control_prenatal(id_paciente, data):
    return supabase.table("control_prenatal").insert({
        "id_paciente": id_paciente,
        "fur": data.get("fur"),
        "fpp": data.get("fpp"),
        "semanas_gestacion": data.get("semanas_gestacion"),
        "riesgo_obstetrico": data.get("riesgo_obstetrico"),
        "riesgo_social": data.get("riesgo_social"),
        "factores_riesgo": data.get("factores_riesgo"),
        "consultas_otorgadas": data.get("consultas_otorgadas"),
        "estado_salud": data.get("estado_salud")
    }).execute()