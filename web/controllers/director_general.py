from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from services.dashboard_service import get_dashboard_stats, get_actividad_reciente, get_estadistica_dashboard

director_general_bp = Blueprint('director_general', __name__)

@director_general_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] != 'director_general'	:
        return redirect(url_for('auth.login'))
    
    stats = get_dashboard_stats()
    actividad_reciente = get_actividad_reciente()
    estadistica_dashboard = get_estadistica_dashboard()
    
    return render_template('direccion/dashboard.html', stats_data=stats, actividad_reciente=actividad_reciente, estadistica_dashboard=estadistica_dashboard)
    
