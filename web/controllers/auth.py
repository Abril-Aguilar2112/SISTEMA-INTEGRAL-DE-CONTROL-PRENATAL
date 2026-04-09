from flask import Blueprint, request, render_template, redirect, url_for, session
from models.auth import LoginRequest
from services.auth_service import login_user, register_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo'].strip().lower()
        password = request.form['password'].strip()

        response = login_user(LoginRequest(correo=correo, password=password))

        if response.get('error') == 'Invalid login credentials':
            response['error'] = 'Credenciales inválidas'
            return render_template('login.html', response=response, rol=None)

        if response.get('data'):
            session['token'] = response.get('data').get('access_token')
            session['nombre'] = response.get('data').get('nombre')
            session['user_id'] = response.get('data').get('id_usuario')
            session['rol'] = response.get('data').get('rol')
            session['correo'] = response.get('data').get('correo')

            roles_permitidos = ['director_general', 'medico', 'enfermera', 'trabajo_social']
            if session.get('rol') in roles_permitidos:
                return redirect(url_for('dashboard.dashboard'))

    return render_template('login.html', response=None, rol=None)	

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
