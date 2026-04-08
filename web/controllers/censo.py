from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
from services.censo_service import get_censo_tabla, get_censo_reporte, actualizar_censo
from models.censo import CensoReporteUpdate

censo_bp = Blueprint("censo", __name__)

@censo_bp.route("/censo")
def censo():
    if 'user_id' not in session or session.get('rol') != 'director_general':
        return redirect(url_for('auth.login'))
        
    censo = get_censo_tabla()
    if censo["message"] == "success":
        return render_template("direccion/censo.html", censo=censo["data"])
    else:
        return render_template("direccion/censo.html", error=censo["error"])

@censo_bp.route('/censo/censo_detalle/<int:id_paciente>')
def censo_detalle(id_paciente):
    if 'user_id' not in session or session.get('rol') != 'director_general':
        return redirect(url_for('auth.login'))
        
    censo = get_censo_reporte(id_paciente)
    today_date = datetime.now().strftime('%d/%m/%Y')
    if censo["message"] == "success":
        return render_template("direccion/censo_detalle.html", id_paciente=id_paciente, censo=censo, today_date=today_date)
    else:
        return render_template("direccion/censo_detalle.html", id_paciente=id_paciente, error=censo["error"], today_date=today_date)

@censo_bp.route('/censo/censo_actualizar/<int:id_paciente>', methods=['POST'])
def censo_actualizar(id_paciente):
    if 'user_id' not in session or session.get('rol') != 'director_general':
        return jsonify({"status": "error", "message": "No tiene permisos para realizar esta acción"}), 403
        
    try:
        data = request.form.to_dict()
        
        if 'mes_reporte' in data:
            pass

        for key in ['id_paciente', 'edad', 'semanas_gestacion', 'gestas', 'partos', 'cesareas', 'abortos', 'consultas_otorgadas', 'semana_epidemiologica']:
            if key in data and data[key]:
                data[key] = int(data[key])
            elif key in data and not data[key]:
                data[key] = 0
        
        censo_update = CensoReporteUpdate(**data)
        
        resultado = actualizar_censo(id_paciente, censo_update.to_rpc())
        
        if resultado["message"] == "success":
            return jsonify({"status": "success", "message": "Censo actualizado correctamente"})
        else:
            error_msg = resultado["error"]
            if "paciente_curp_key" in error_msg:
                error_msg = "Ya existe un paciente con este CURP registrado."
            elif "23505" in error_msg:
                error_msg = "Ya existe un registro con estos datos únicos."
                
            return jsonify({"status": "error", "message": error_msg}), 400
            
    except Exception as e:
        error_msg = str(e)
        if "paciente_curp_key" in error_msg:
            error_msg = "Ya existe un paciente con este CURP registrado."
        return jsonify({"status": "error", "message": error_msg}), 400
