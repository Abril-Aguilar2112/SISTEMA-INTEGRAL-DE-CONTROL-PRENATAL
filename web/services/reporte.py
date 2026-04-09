from utils.supabase_client import supabase
import json

def serialize_dates(data):
    if isinstance(data, list):
        return [serialize_dates(i) for i in data]
    if isinstance(data, dict):
        return {k: serialize_dates(v) for k, v in data.items()}
    if hasattr(data, 'isoformat'):
        return data.isoformat()
    return data

def get_reportes(generado_por=None):
    try:
        query = supabase.table('reporte').select("*")
        if generado_por:
            if isinstance(generado_por, list):
                query = query.in_('generado_por', generado_por)
            else:
                query = query.eq('generado_por', generado_por)
        
        response = query.execute()
        data = response.data or []
        
        for r in data:
            if r.get('datos') and isinstance(r['datos'], str):
                r['datos'] = json.loads(r['datos'])
        
        data = serialize_dates(data)
        
        return {
            "data": data,
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": [],
            "message": "error",
            "error": str(e)
        }

def get_reportes_by_usuario(id_usuario):
    try:
        response = supabase.table('reporte').select("*").execute()
        return {
            "data": response.data or [],
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": [],
            "message": "error",
            "error": str(e)
        }

def get_reporte_by_id(id_reporte):
    try:
        response = supabase.table('reporte').select("*").eq('id_reporte', id_reporte).execute()
        data = response.data[0] if response.data else None
        
        # Aseguramos que 'datos' sea un diccionario
        if data and data.get('datos') and isinstance(data['datos'], str):
            data['datos'] = json.loads(data['datos'])
            
        data = serialize_dates(data)
            
        return {
            "data": data,
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": None,
            "message": "error",
            "error": str(e)
        }

def precarga_reporte_direccion():
    try:
        response = supabase.table('vista_precarga_director').select("*").execute()
        return {
            "data": response.data or [],
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": [],
            "message": "error",
            "error": str(e)
        }

def precarga_reporte_enfermeria():
    try:
        response = supabase.table('vista_precarga_enfermera').select("*").execute()
        return {
            "data": response.data or [],
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": [],
            "message": "error",
            "error": str(e)
        }
    
def precarga_censo_nominal():
    try:
        response = supabase.from_('vista_censo_tabla').select("*").execute()
        return {
            "data": response.data or [],
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": [],
            "message": "error",
            "error": str(e)
        }
    
def precarga_reporte_medico():
    try:
        response = supabase.table('vista_precarga_medico_resumen').select("*").execute()
        return {
            "data": response.data or [],
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": [],
            "message": "error",
            "error": str(e)
        }

def precarga_medico_pacientes():
    try:
        response = supabase.table('vista_precarga_medico_pacientes').select("*").execute()
        return {
            "data": response.data or [],
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": [],
            "message": "error",
            "error": str(e)
        }

def precarga_ts_resumen():
    try: 
        response = supabase.table('vista_precarga_ts_resumen').select("*").execute()
        return {
            "data": response.data or [],
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": [],
            "message": "error",
            "error": str(e)
        }

def precarga_ts_casos():
    try: 
        response = supabase.table('vista_precarga_ts_casos').select("*").execute()
        return {
            "data": response.data or [],
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": [],
            "message": "error",
            "error": str(e)
        }

def create_reporte(data):
    try:
        datos_completos = data.get('datos', {})
        datos_completos['estado'] = data.get('estado')
        
        insert_data = {
            "id_usuario": data.get('id_usuario'),
            "periodo_inicio": data.get('periodo_inicio'),
            "periodo_fin": data.get('periodo_fin'),
            "generado_por": data.get('generado_por'),
            "tipo": data.get('tipo'),
            "datos": datos_completos
        }
        
        response = supabase.table('reporte').insert(insert_data).execute()
        
        return {
            "data": response.data[0] if response.data else None,
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": None,
            "message": "error",
            "error": str(e)
        }

def update_reporte(id_reporte, data):
    try:
        current = get_reporte_by_id(id_reporte)
        if current['error'] or not current['data']:
            return current
            
        current_datos = current['data'].get('datos') or {}
        
        if 'estado' in data:
            current_datos['estado'] = data['estado']
        if 'datos' in data:
            current_datos.update(data['datos'])
            
        update_data = {
            "datos": current_datos
        }

        response = supabase.table('reporte').update(update_data).eq('id_reporte', id_reporte).execute()
        
        return {
            "data": response.data[0] if response.data else None,
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": None,
            "message": "error",
            "error": str(e)
        }

def delete_reporte(id_reporte):
    try:
        response = supabase.table('reporte').delete().eq('id_reporte', id_reporte).execute()
        return {
            "data": response.data,
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": None,
            "message": "error",
            "error": str(e)
        }

def get_ultimo_reporte_por_rol(rol):
    try:
        response = supabase.table('reporte')\
            .select("*")\
            .eq('generado_por', rol)\
            .order('fecha', desc=True)\
            .limit(1)\
            .execute()
            
        data = response.data[0] if response.data else None
        
        if data and data.get('datos') and isinstance(data['datos'], str):
            data['datos'] = json.loads(data['datos'])
            
        data = serialize_dates(data)
            
        return {
            "data": data,
            "message": "success",
            "error": None
        }
    except Exception as e:
        return {
            "data": None,
            "message": "error",
            "error": str(e)
        }
