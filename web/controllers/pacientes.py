from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from services.paciente_service import get_pacientes

pacientes_bp = Blueprint('pacientes', __name__)

@pacientes_bp.route('/pacientes', methods=['GET'])
def pacientes():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] != 'director_general'	:
        return redirect(url_for('auth.login'))

    page = int(request.args.get('page', 1))
    search = request.args.get('search', '')
    riesgo = request.args.get('riesgo', '')
    semanas = request.args.get('semanas', '')

    result = get_pacientes(
        page=page,
        search=search,
        riesgo=riesgo,
        semanas=semanas
    )


    return render_template('direccion/pacientes/pacientes.html', pacientes=result)
