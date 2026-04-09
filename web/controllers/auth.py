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
            return render_template('login.html', response=response)

        if response.get('data'):
            session['token'] = response.get('data').get('access_token')
            session['nombre'] = response.get('data').get('nombre')
            session['user_id'] = response.get('data').get('id_usuario')
            session['rol'] = response.get('data').get('rol')
            session['correo'] = response.get('data').get('correo')

            if session.get('rol') == 'director_general':
                return redirect(url_for('dashboard.dashboard'))

    return render_template('login.html', response=None)	

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
