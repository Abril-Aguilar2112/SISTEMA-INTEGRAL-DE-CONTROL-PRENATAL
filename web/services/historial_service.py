from utils.supabase_client import supabase

def crear_historial(id_paciente, data):
    return supabase.table("historial_clinico").insert({
        "id_paciente": id_paciente,
        "antecedentes": data.get("antecedentes"),
        "observaciones": data.get("observaciones")
    }).execute()