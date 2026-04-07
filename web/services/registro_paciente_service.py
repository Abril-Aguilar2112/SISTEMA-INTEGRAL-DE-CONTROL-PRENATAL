from utils.supabase_client import supabase

def registrar_paciente(data):
    res = supabase.rpc(
        "registrar_paciente_completo",
        data
    ).execute()

    return res.data