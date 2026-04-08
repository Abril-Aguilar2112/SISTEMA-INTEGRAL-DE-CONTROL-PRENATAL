from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from pydantic import ValidationError
from services.paciente_service import get_pacientes, get_paciente_by_id, registrar_paciente, actualizar_paciente
from models.paciente import PacienteCreate, PacienteUpdate

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

@pacientes_bp.route("/paciente_registro", methods=["GET", "POST"])
def paciente_registro():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] not in ['director_general', 'enfermera']	:
        return redirect(url_for('auth.login'))
    if request.method == "GET":
        return render_template("direccion/pacientes/paciente_registro.html")
 
    try:
        paciente = PacienteCreate(**request.form)
        result   = registrar_paciente(paciente.to_rpc())
 
        if result and result.get("ok"):
            return redirect(url_for("pacientes.pacientes"))
 
        if result.get("error"):
            error = result.get("error", "Error al registrar")
        return render_template("direccion/pacientes/paciente_registro.html", error=error)

    except ValidationError as e:
        flash(str(e), "error")
        return render_template("direccion/pacientes/paciente_registro.html", error=str(e))

@pacientes_bp.route("/paciente_editar/<int:id_paciente>", methods=["GET", "POST"])
def paciente_editar(id_paciente):

    if request.method == "GET":
        paciente = get_paciente_by_id(id_paciente)["data"]

        if paciente.get("error"):
            return redirect(url_for("pacientes.pacientes"))

        return render_template('direccion/pacientes/paciente_editar.html', paciente=paciente, id_paciente=id_paciente, error=None)

    try:
        form_data = request.form.to_dict()
        form_data['id_paciente'] = id_paciente

        paciente = get_paciente_by_id(id_paciente)["data"]

        paciente_update = PacienteUpdate(**form_data)

        result = actualizar_paciente(paciente_update.to_rpc())

        if result and result.get("ok"):
            return redirect(url_for("pacientes.pacientes"))
 
        error = result.get("error") if result else "Error desconocido"
    
        return render_template('direccion/pacientes/paciente_editar.html', paciente=paciente, id_paciente=id_paciente, error=error)

    except ValidationError as e:
        error = str(e)
        return render_template('direccion/pacientes/paciente_editar.html', paciente=paciente, id_paciente=id_paciente, error=error)

    except Exception as e:
        return render_template('direccion/pacientes/paciente_editar.html', paciente=paciente, id_paciente=id_paciente, error=error)

@pacientes_bp.route("/paciente_detalle/<int:id_paciente>", methods=["GET"])
def paciente_detalle(id_paciente):
    paciente = get_paciente_by_id(id_paciente)["data"]
    print(paciente)
    return render_template('direccion/pacientes/paciente_detalle.html', paciente=paciente)

