from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from services.paciente_service import get_pacientes

pacientes_bp = Blueprint('pacientes', __name__)

@pacientes_bp.route('/pacientes')
def pacientes():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] != 'director_general'	:
        return redirect(url_for('auth.login'))
    return render_template('direccion/pacientes/pacientes.html')