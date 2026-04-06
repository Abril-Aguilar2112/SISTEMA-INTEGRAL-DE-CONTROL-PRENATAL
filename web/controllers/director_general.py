from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template

director_general_bp = Blueprint('director_general', __name__)

@director_general_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] != 'director_general'	:
        return redirect(url_for('auth.login'))


    return render_template('direccion/dashboard.html')
    
