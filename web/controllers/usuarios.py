from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from services.usuarios import get_usuarios, get_usuario_by_id, update_usuario, create_usuario
from services.auth_service import register_user, update_password
from models.auth import UserRegistration

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuarios', methods=['GET'])
def usuarios():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] != 'director_general':
        return redirect(url_for('dashboard.dashboard'))
    
    # Obtener parámetros de filtrado
    search = request.args.get('search')
    rol = request.args.get('rol')
    estado = request.args.get('estado')
    
    # Convertir estado a booleano si existe
    estado_bool = None
    if estado == '1':
        estado_bool = True
    elif estado == '0':
        estado_bool = False
    
    usuarios_list = get_usuarios(search=search, rol=rol, estado=estado_bool)
    if usuarios_list['error']:
        flash(f"Error al obtener usuarios: {usuarios_list['error']}", 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('direccion/usuarios/usuarios.html', usuarios=usuarios_list['data'])

@usuarios_bp.route('/usuarios/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] != 'director_general':
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            correo = request.form.get('correo')
            password = request.form.get('password')
            rol = request.form.get('rol')
            
            user_data = UserRegistration(
                nombre=nombre,
                correo=correo,
                password=password,
                rol=rol
            )
            
            # 1. Registrar en Supabase Auth
            auth_result = register_user(user_data)
            
            if auth_result['error']:
                flash(auth_result['error'], 'error')
                return render_template('direccion/usuarios/crear_usuario.html')
            
            auth_id = auth_result['data']['auth_id']
            
            # 2. Guardar en la base de datos (Supabase Table)
            db_data = {
                "auth_id": auth_id,
                "nombre": nombre,
                "correo": correo,
                "rol": rol
            }
            
            db_result = create_usuario(db_data)
            
            if db_result['error']:
                flash(db_result['error'], 'error')
                return render_template('direccion/usuarios/crear_usuario.html')
            
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('usuarios.usuarios'))
            
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')
            return render_template('direccion/usuarios/crear_usuario.html')

    return render_template('direccion/usuarios/crear_usuario.html')

@usuarios_bp.route('/usuarios/editar_usuario/<int:id_usuario>', methods=['GET', 'POST'])
def editar_usuario(id_usuario):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] != 'director_general':
        return redirect(url_for('dashboard.dashboard'))

    usuario = get_usuario_by_id(id_usuario)
    if usuario['error'] or not usuario['data']:
        flash('Error al obtener usuario', 'error')
        return redirect(url_for('usuarios.usuarios'))

    if request.method == 'POST':
        try:
            data = {}

            nombre = request.form.get('nombre')
            correo = request.form.get('correo')
            rol = request.form.get('rol')
            estado_raw = request.form.get('estado')
            estado = (estado_raw == '1') if estado_raw is not None else None
            telefono = request.form.get('telefono')
            password = request.form.get('password')
            confirmPassword = request.form.get('confirm_password')

            if nombre and nombre != usuario['data']['nombre']:
                data['nombre'] = nombre
            if correo and correo != usuario['data']['correo']:
                data['correo'] = correo
            if rol and rol != usuario['data']['rol']:
                data['rol'] = rol
            
            if estado is not None and estado != usuario['data'].get('estado'):
                data['estado'] = estado
            
            if telefono is not None and telefono != usuario['data'].get('telefono'):
                data['telefono'] = telefono
            
            if password:
                if password != confirmPassword:
                    flash('Las contraseñas no coinciden', 'error')
                    return redirect(url_for('usuarios.editar_usuario', id_usuario=id_usuario))
                
                auth_response = update_password(password)
                if auth_response.get('error'):
                    flash(auth_response['error'], 'error')
                    return redirect(url_for('usuarios.editar_usuario', id_usuario=id_usuario))
            
            if not data and not password:
                flash('No hay cambios para actualizar', 'info')
                return redirect(url_for('usuarios.usuarios'))

            result = update_usuario(id_usuario, data)
            
            if result['error']:
                flash(result['error'], 'error')
                return redirect(url_for('usuarios.editar_usuario', id_usuario=id_usuario))
            
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('usuarios.usuarios'))
            
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')
            return redirect(url_for('usuarios.editar_usuario', id_usuario=id_usuario))
    
    return render_template('direccion/usuarios/editar_usuario.html', usuario=usuario['data'])

@usuarios_bp.route('/usuarios/cambiar_estado/<int:id_usuario>/<int:estado_actual>', methods=['GET'])
def cambiar_estado_usuario(id_usuario, estado_actual):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] != 'director_general':
        return redirect(url_for('dashboard.dashboard'))
    
    nuevo_estado = not bool(estado_actual)
    update_data = {"estado": nuevo_estado}
    result = update_usuario(id_usuario, update_data)
    
    if result['error']:
        flash(f"Error al cambiar estado: {result['error']}", 'error')
    else:
        mensaje = 'Usuario activado correctamente' if nuevo_estado else 'Usuario desactivado correctamente'
        flash(mensaje, 'success')
        
    return redirect(url_for('usuarios.usuarios'))