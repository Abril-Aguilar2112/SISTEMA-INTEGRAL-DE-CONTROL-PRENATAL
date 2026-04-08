from flask import Blueprint, render_template, session, redirect, url_for, request
from services.inasistencia_service import get_inasistencias as get_inasistencias_service
from services.inasistencia_service import actualizar_inasistencia as actualizar_inasistencia_service
from models.inasistencia import InasistenciaContestar

inasistencias_bp = Blueprint('inasistencias', __name__)

@inasistencias_bp.route('/inasistencias')
def get_inasistencias():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] != 'director_general'	:
        return redirect(url_for('auth.login'))

    search = request.args.get('search')
    estado = request.args.get('estatus')
    fecha = request.args.get('fecha')
    justificada = request.args.get('justificada')

    inasistencias = get_inasistencias_service(search, estado, fecha, justificada)

    if inasistencias.get("error"):
        return render_template('direccion/inasistencias.html', inasistencias=inasistencias)
    return render_template('direccion/inasistencias.html', inasistencias=inasistencias)

@inasistencias_bp.route('/inasistencias/actualizar_inasistencia/<int:id_inasistencia>', methods=['POST']) 
def actualizar_inasistencia(id_inasistencia):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] != 'director_general'	:
        return redirect(url_for('auth.login'))

    form = {}
    form['observacion_ts'] = request.form.get('observacion_ts')
    form['mensaje_seguimiento'] = request.form.get('mensaje_seguimiento')

    data = InasistenciaContestar(**form).model_dump(mode="json")

    response = actualizar_inasistencia_service(data, id_inasistencia=id_inasistencia)

    if response.get('error'):   
        return redirect(url_for('inasistencias.get_inasistencias'))
    return redirect(url_for('inasistencias.get_inasistencias'))


