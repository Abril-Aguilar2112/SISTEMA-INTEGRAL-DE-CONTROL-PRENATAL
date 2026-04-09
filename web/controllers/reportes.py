from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, Response
from services.reporte import (
    get_reportes, get_reportes_by_usuario, get_reporte_by_id, 
    create_reporte, precarga_reporte_enfermeria, precarga_censo_nominal,
    update_reporte, delete_reporte, precarga_reporte_direccion, 
    precarga_reporte_medico, precarga_medico_pacientes, get_ultimo_reporte_por_rol,
    precarga_ts_resumen, precarga_ts_casos
)
from models.reporte import ReporteCreate, ReporteUpdate
from pydantic import ValidationError
import csv
import io

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/reportes')
def reportes():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('reportes/ver_reportes.html', rol=session.get('rol'))

@reportes_bp.route('/reportes/crear_reporte')
def crear_reporte():
    roles_permitidos = ['director_general', 'medico', 'enfermera', 'trabajo_social']
    if 'user_id' not in session or session.get('rol') not in roles_permitidos:
        return redirect(url_for('auth.login'))
    
    precarga = None
    result = {'error': None, 'data': None}
    
    if session.get('rol') == 'director_general':
        result = precarga_reporte_direccion()
    elif session.get('rol') == 'medico':
        res_med = precarga_reporte_medico()
        res_pacientes = precarga_medico_pacientes()
        
        precarga = {
            'resumen': res_med['data'][0] if not res_med['error'] and res_med['data'] else None,
            'pacientes': res_pacientes['data'] if not res_pacientes['error'] and res_pacientes['data'] else []
        }
    elif session.get('rol') == 'enfermera':
        res_enf = precarga_reporte_enfermeria()
        res_censo = precarga_censo_nominal()
        
        precarga = {
            'resumen': res_enf['data'][0] if not res_enf['error'] and res_enf['data'] else None,
            'censo': res_censo['data'] if not res_censo['error'] and res_censo['data'] else []
        }
    elif session.get('rol') == 'trabajo_social':
        res_resumen = precarga_ts_resumen()
        res_casos = precarga_ts_casos()
        
        precarga = {
            'resumen': res_resumen['data'][0] if not res_resumen['error'] and res_resumen['data'] else None,
            'casos': res_casos['data'] if not res_casos['error'] and res_casos['data'] else []
        }
    
    return render_template('reportes/reportes_crear.html', rol=session.get('rol'), precarga=precarga)

@reportes_bp.route('/api/reportes', methods=['GET'])
def api_get_reportes():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    rol_sesion = session.get('rol')
    
    # Lógica de filtrado por área/rol
    generado_por_filtro = None
    if rol_sesion == 'enfermera':
        # Enfermera ve sus reportes y los de trabajo social
        generado_por_filtro = ['enfermera', 'trabajo_social']
    elif rol_sesion != 'director_general':
        # Otros roles solo ven los de su área
        generado_por_filtro = rol_sesion
            
    # Si se pasó un filtro por query param, lo respetamos si es permitido
    rol_param = request.args.get('generado_por')
    if rol_param:
        if rol_sesion == 'director_general':
            generado_por_filtro = rol_param
        elif rol_sesion == 'enfermera' and rol_param in ['enfermera', 'trabajo_social']:
            generado_por_filtro = rol_param
    
    estado = request.args.get('estado')
    
    result = get_reportes(generado_por=generado_por_filtro)
    if result['error']:
        return jsonify(result), 500
        
    data = result['data']
    
    if estado:
        # Usamos (r.get('datos') or {}) para manejar casos donde 'datos' sea None en la DB
        data = [r for r in data if (r.get('datos') or {}).get('estado') == estado]
        
    return jsonify({"data": data, "message": "success"}), 200

@reportes_bp.route('/api/reportes', methods=['POST'])
def api_create_reporte():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        data = request.get_json()
        
        if not data.get('id_usuario') or data.get('id_usuario') in ['null', 'NaN', '']:
            data['id_usuario'] = session.get('user_id')
            
        reporte_validado = ReporteCreate(**data)
        result = create_reporte(reporte_validado.model_dump(mode='json'))
        
        if result['error']:
            return jsonify(result), 500
        return jsonify(result['data']), 201
        
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            field = error['loc'][0]
            msg = error['msg']
            error_messages.append(f"Campo {field}: {msg}")
        return jsonify({"error": "; ".join(error_messages)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route('/api/reportes/<int:id_reporte>', methods=['GET'])
def api_get_reporte(id_reporte):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    result = get_reporte_by_id(id_reporte)
    if result['error']:
        return jsonify(result), 500
    if not result['data']:
        return jsonify({"error": "Reporte no encontrado"}), 404
    return jsonify(result['data']), 200

@reportes_bp.route('/api/reportes/<int:id_reporte>', methods=['PATCH'])
def api_update_reporte(id_reporte):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        data = request.get_json()
        reporte_update = ReporteUpdate(**data)
        result = update_reporte(id_reporte, reporte_update.model_dump(exclude_unset=True))
        
        if result['error']:
            return jsonify(result), 500
        return jsonify(result['data']), 200
        
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            field = error['loc'][0]
            msg = error['msg']
            error_messages.append(f"Campo {field}: {msg}")
        return jsonify({"error": "; ".join(error_messages)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route('/api/reportes/ultimo/<string:rol>', methods=['GET'])
def api_get_ultimo_reporte(rol):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    result = get_ultimo_reporte_por_rol(rol)
    if result['error']:
        return jsonify(result), 500
    return jsonify(result['data']), 200

@reportes_bp.route('/api/reportes/<int:id_reporte>/descargar', methods=['GET'])
def descargar_reporte_csv(id_reporte):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    result = get_reporte_by_id(id_reporte)
    if result['error'] or not result['data']:
        return jsonify({"error": "Reporte no encontrado"}), 404
        
    reporte = result['data']
    datos = reporte.get('datos', {})
    rol = reporte.get('generado_por')
    tipo = reporte.get('tipo')
    
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    
    writer.writerow(['REPORTE DE CONTROL PRENATAL - SIGEP'])
    writer.writerow(['ID Reporte', reporte.get('id_reporte')])
    writer.writerow(['Tipo', tipo.replace('_', ' ').upper()])
    writer.writerow(['Generado por', rol.replace('_', ' ').upper()])
    writer.writerow(['Período', f"{reporte.get('periodo_inicio')} a {reporte.get('periodo_fin')}"])
    writer.writerow(['Fecha de Creación', reporte.get('fecha')])
    writer.writerow(['Estado', datos.get('estado', 'N/A').upper()])
    writer.writerow([])
    
    detalles = datos
    
    if rol == 'enfermera':
        writer.writerow(['RESUMEN DE PACIENTES'])
        res = detalles.get('resumen', {})
        writer.writerow(['Total Activas', res.get('total_pacientes_activas')])
        writer.writerow(['Pacientes Nuevas', res.get('pacientes_nuevas')])
        writer.writerow(['En Seguimiento', res.get('pacientes_en_seguimiento')])
        writer.writerow(['Citas Programadas', res.get('citas_programadas')])
        writer.writerow(['Citas Cumplidas', res.get('citas_cumplidas')])
        writer.writerow(['Inasistencias', res.get('inasistencias')])
        writer.writerow([])
        writer.writerow(['CENSO NOMINAL'])
        writer.writerow(['Nombre', 'Edad', 'Semanas', 'Nivel Riesgo', 'Última Atención'])
        for p in detalles.get('censo', []):
            writer.writerow([p.get('nombre'), p.get('edad'), p.get('semanas_gestacion'), p.get('nivel_riesgo'), p.get('fecha_ultima_atencion')])
            
    elif rol == 'medico':
        writer.writerow(['RESUMEN DE CONSULTAS'])
        res = detalles.get('resumen', {})
        writer.writerow(['Consultas Realizadas', res.get('consultas_realizadas')])
        writer.writerow(['Pacientes Atendidas', res.get('pacientes_atendidas')])
        writer.writerow(['Signos de Alarma', res.get('pacientes_con_signos_alarma')])
        writer.writerow([])
        writer.writerow(['PACIENTES ATENDIDAS'])
        writer.writerow(['Nombre', 'Semanas', 'Riesgo', 'Riesgo Obstétrico', 'Consultas', 'Diagnóstico', 'Tratamiento'])
        for p in detalles.get('pacientes', []):
            writer.writerow([p.get('nombre'), p.get('semanas_gestacion'), p.get('nivel_riesgo'), p.get('riesgo_obstetrico'), p.get('consultas_otorgadas'), p.get('diagnostico'), p.get('tratamiento')])

    elif rol == 'trabajo_social':
        writer.writerow(['RESUMEN DE INASISTENCIAS'])
        res = detalles.get('resumen', {})
        writer.writerow(['Total Inasistencias', res.get('total_inasistencias')])
        writer.writerow(['Justificadas', res.get('justificadas')])
        writer.writerow(['Sin Justificación', res.get('sin_justificacion')])
        writer.writerow(['Reintegradas', res.get('pacientes_reintegradas')])
        writer.writerow([])
        writer.writerow(['CASOS REGISTRADOS'])
        writer.writerow(['Nombre', 'Teléfono', 'Fecha Cita', 'Motivo', 'Justificada', 'Observación TS'])
        for c in detalles.get('casos', []):
            writer.writerow([c.get('nombre'), c.get('telefono'), c.get('fecha_cita'), c.get('motivo'), 'SÍ' if c.get('justificada') else 'NO', c.get('observacion_ts')])

    elif rol == 'director_general':
        writer.writerow(['INDICADORES CLAVE (KPIs)'])
        kpis = detalles.get('kpis', {})
        writer.writerow(['Total Pacientes Activas', kpis.get('total_pacientes_activas')])
        writer.writerow(['Consultas del Mes', kpis.get('consultas_mes')])
        writer.writerow(['Tasa de Asistencia (%)', kpis.get('tasa_asistencia')])
        writer.writerow(['Pacientes Alto Riesgo', kpis.get('pacientes_alto_riesgo')])
        writer.writerow([])
        writer.writerow(['DISTRIBUCIÓN DE RIESGO'])
        riesgo = detalles.get('distribucion_riesgo', {})
        writer.writerow(['Bajo', riesgo.get('bajo')])
        writer.writerow(['Medio', riesgo.get('medio')])
        writer.writerow(['Alto', riesgo.get('alto')])
        if detalles.get('alertas'):
            writer.writerow([])
            writer.writerow(['ALERTAS ACTIVAS'])
            for a in detalles.get('alertas', []):
                writer.writerow([a])

    filename = f"reporte_{tipo}_{reporte.get('periodo_inicio')}.csv"
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@reportes_bp.route('/api/reportes/<int:id_reporte>', methods=['DELETE'])
def api_delete_reporte(id_reporte):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    result = delete_reporte(id_reporte)
    if result['error']:
        return jsonify(result), 500
    return jsonify({"message": "Reporte eliminado"}), 200
