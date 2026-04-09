from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.citas import get_citas, get_cita_by_id, update_cita, upsert_inasistencia,set_estado_cita, get_stats_citas, crear_cita
from services.medico import get_medicos
from services.paciente_service import get_pacientes
from models.cita import CitaUpdate, CitaReagendar, CitaCreate
from pydantic import ValidationError

citas_bp = Blueprint('citas', __name__)

@citas_bp.route('/citas')
def citas():
    if 'user_id' not in session or session.get('rol') not in ['director_general', 'medico', 'trabajo_social']:
        return redirect(url_for('auth.login'))
        
    search = request.args.get("search")
    fecha = request.args.get("fecha")
    estado = request.args.get("estado")

    if session['rol'] == 'medico':
        id_medico = session['user_id']
        citas = get_citas(search, fecha, estado, id_medico)
    else:
        citas = get_citas(search, fecha, estado)

    stats = get_stats_citas()
    return render_template('direccion/citas/citas.html', citas=citas, stats=stats, rol=session['rol'])  

@citas_bp.route('/cita_crear', methods=['GET', 'POST'])
def cita_crear():
    if 'user_id' not in session or session.get('rol') not in ['director_general', 'medico']:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            form_data = request.form.to_dict()
            
            # Soporte para formularios cacheados que aún usen 'tipo_consulta'
            if 'tipo_consulta' in form_data and 'area' not in form_data:
                form_data['area'] = form_data.pop('tipo_consulta')
                
            # Validar y formatear con Pydantic
            cita_valida = CitaCreate(**form_data)
            
            result = crear_cita(cita_valida.model_dump(mode="json"))
            
            if result["message"] == "success":
                flash("Cita programada exitosamente", "success")
                return redirect(url_for("citas.citas"))
            else:
                flash(f"Error al crear cita: {result['error']}", "error")
        except ValidationError as e:
            flash(f"Error de validación: {str(e)}", "error")
        except Exception as e:
            flash(f"Ocurrió un error inesperado: {str(e)}", "error")

    medicos = get_medicos()
    pacientes = get_pacientes(per_page=1000)
        
    return render_template('direccion/citas/cita_crear.html', medicos=medicos, pacientes=pacientes, rol=session['rol'])

@citas_bp.route('/cita_editar/<int:id_cita>', methods=['GET', 'POST'])
def cita_editar(id_cita):
    if 'user_id' not in session or session.get('rol') not in ['director_general', 'medico']:
        return redirect(url_for('auth.login'))
        
    if request.method == 'GET':
        cita = get_cita_by_id(id_cita)
        medicos = get_medicos()
        return render_template('direccion/citas/cita_editar.html', id_cita=id_cita, cita=cita, medicos=medicos, rol=session['rol'])

    if request.method == 'POST':
        try:
            form = request.form.to_dict()
            cita_formateada = CitaUpdate(**form).model_dump(mode="json", exclude_none=True)

            result = update_cita(cita_formateada, id_cita)
            if result["message"] == "success":
                flash("Cita reagendada exitosamente", "success")
                return redirect(url_for("citas.citas"))
            else:
                flash(result["error"], "error")
                cita = get_cita_by_id(id_cita)
                medicos = get_medicos()
                return render_template('direccion/citas/cita_editar.html', id_cita=id_cita, cita=cita, medicos=medicos, error=result["error"], rol=session['rol'])

        except ValidationError as e:
            flash(f"Error de validación: {str(e)}", "error")
            return redirect(url_for("citas.cita_editar", id_cita=id_cita))
        except Exception as e:
            flash(f"Ocurrió un error inesperado: {str(e)}", "error")
            return redirect(url_for("citas.cita_editar", id_cita=id_cita))

@citas_bp.route('/reagendar/<int:id_cita>', methods=['POST'])
def reagendar_cita(id_cita):
    if 'user_id' not in session or session.get('rol') not in ['director_general', 'medico']:
        return jsonify({"status": "error", "message": "No tiene permisos para realizar esta acción"}), 403
    try:
        form = request.form.to_dict()
        cita_formateada = CitaReagendar(**form).model_dump(mode="json", exclude_none=True)
        hora = cita_formateada.get("hora")
        if isinstance(hora, str) and len(hora) == 5:
            cita_formateada["hora"] = f"{hora}:00"
        cita_formateada["estado"] = "reprogramada"

        result = update_cita(cita_formateada, id_cita)
        if result["message"] == "success":
            flash("Cita reagendada exitosamente", "success")
            return redirect(url_for("citas.citas"))
        flash(result["error"], "error")
        return redirect(url_for("citas.citas"))
    except ValidationError as e:
        flash(f"Error de validación: {str(e)}", "error")
        return redirect(url_for("citas.citas"))
    except Exception as e:
        flash(f"Ocurrió un error inesperado: {str(e)}", "error")
        return redirect(url_for("citas.citas"))


@citas_bp.route('/justificar/<int:id_cita>', methods=['POST'])
def justificar_cita(id_cita):
    if 'user_id' not in session or session.get('rol') not in ['director_general']:
        return redirect(url_for('auth.login'))
    try:
        motivo = (request.form.get("motivo") or "").strip()
        if not motivo:
            flash("Motivo obligatorio", "error")
            return redirect(url_for("citas.citas"))

        upsert_result = upsert_inasistencia(id_cita=id_cita, motivo=motivo, justificada=True)
        if upsert_result["error"] is not None:
            flash(upsert_result["error"], "error")
            return redirect(url_for("citas.citas"))

        result = update_cita({"estado": "justificada"}, id_cita)
        if result["message"] == "success":
            flash("Inasistencia justificada", "success")
            return redirect(url_for("citas.citas"))
        flash(result["error"], "error")
        return redirect(url_for("citas.citas"))
    except Exception as e:
        flash(f"Ocurrió un error inesperado: {str(e)}", "error")
        return redirect(url_for("citas.citas"))

@citas_bp.route('/cita/estado/<int:id_cita>', methods=['POST'])
def set_cita_estado(id_cita):
    if 'user_id' not in session or session.get('rol') not in ['director_general', 'medico']:
        return jsonify({"status": "error", "message": "No tiene permisos para realizar esta acción"}), 403
    if request.method == 'POST':
        try:
            estado = request.form.get('estado')
            result = set_estado_cita(id_cita, estado)
            if result["message"] == "success":
                flash("Cita actualizada exitosamente", "success")
                return redirect(url_for("citas.citas"))
            flash(result["error"], "error")
            return redirect(url_for("citas.citas"))
        except Exception as e:
            flash(f"Ocurrió un error inesperado: {str(e)}", "error")
            return redirect(url_for("citas.citas"))
    

       
