let currentReporteId = null;
let reporteDataActual = null;
let alertas = [];
let currentReporteJson = null;

function renderFormularioPorRol(rol) {
    document.querySelectorAll('.formulario-rol').forEach(el => el.classList.remove('activo'));
    
    const roleNames = {
        'enfermera': 'Enfermera',
        'medico': 'Médico',
        'trabajo_social': 'Trabajo Social',
        'director_general': 'Director General'
    };
    
    const userRolElement = document.getElementById('userRol');
    if (userRolElement) {
        userRolElement.textContent = roleNames[rol] || rol;
    }
    
    const tipoLabels = {
        'enfermera': 'Censo Mensual',
        'medico': 'Seguimiento Clínico',
        'trabajo_social': 'Análisis de Inasistencias',
        'director_general': 'Dirección'
    };
    const tipoReporteLabel = document.getElementById('tipoReporteLabel');
    if (tipoReporteLabel) {
        tipoReporteLabel.textContent = tipoLabels[rol] || '-';
    }
    
    let formId = '';
    switch(rol) {
        case 'enfermera': formId = 'formularioEnfermera'; break;
        case 'medico': formId = 'formularioMedico'; break;
        case 'trabajo_social': formId = 'formularioTrabajoSocial'; break;
        case 'director_general': formId = 'formularioDirector'; break;
    }
    
    if (formId) {
        const formElement = document.getElementById(formId);
        if (formElement) {
            formElement.classList.add('activo');
        }
    }

    if (rol === 'director_general' && typeof PRECARGA_DATA !== 'undefined' && PRECARGA_DATA) {
        aplicarPrecargaDirector(PRECARGA_DATA);
        cargarDatosReporteAnterior(rol);
    } else if (rol === 'enfermera' && typeof PRECARGA_DATA !== 'undefined' && PRECARGA_DATA) {
        aplicarPrecargaEnfermera(PRECARGA_DATA);
        cargarDatosReporteAnterior(rol);
    } else if (rol === 'medico' && typeof PRECARGA_DATA !== 'undefined' && PRECARGA_DATA) {
        aplicarPrecargaMedico(PRECARGA_DATA);
        cargarDatosReporteAnterior(rol);
    }
    
    actualizarJsonPreview();
}

async function cargarDatosReporteAnterior(rol) {
    try {
        const response = await fetch(`/gestion/api/reportes/ultimo/${rol}`);
        if (!response.ok) return;
        
        const lastReport = await response.json();
        if (!lastReport || !lastReport.datos) return;

        if (rol === 'director_general') {
            const d = lastReport.datos;
            const kpis = d.kpis || {};
            
            const camposAnterior = {
                'dir_total_pacientes_activas_anterior': kpis.total_pacientes_activas,
                'dir_consultas_mes_anterior': kpis.consultas_mes,
                'dir_tasa_asistencia_anterior': kpis.tasa_asistencia,
                'dir_pacientes_alto_riesgo_anterior': kpis.pacientes_alto_riesgo
            };

            for (const [id, value] of Object.entries(camposAnterior)) {
                const el = document.getElementById(id);
                if (el && (!el.value || el.value === '0')) {
                    el.value = value || 0;
                }
            }
            
            calcularVariacionesDirector();
        }
    } catch (error) {
        console.error(error);
    }
}

function calcularVariacionesDirector() {
    const metrics = [
        { current: 'dir_total_pacientes_activas', previous: 'dir_total_pacientes_activas_anterior', variation: 'dir_variacion_pacientes' },
        { current: 'dir_consultas_mes', previous: 'dir_consultas_mes_anterior', variation: 'dir_variacion_consultas' },
        { current: 'dir_tasa_asistencia', previous: 'dir_tasa_asistencia_anterior', variation: 'dir_variacion_asistencia' }
    ];

    metrics.forEach(m => {
        const curVal = parseFloat(document.getElementById(m.current)?.value) || 0;
        const preVal = parseFloat(document.getElementById(m.previous)?.value) || 0;
        const varEl = document.getElementById(m.variation);

        if (varEl && preVal > 0) {
            const diff = ((curVal - preVal) / preVal) * 100;
            const sign = diff >= 0 ? '+' : '';
            varEl.value = `${sign}${diff.toFixed(1)}%`;
            varEl.style.color = diff >= 0 ? '#10b981' : '#ef4444';
        } else if (varEl) {
            varEl.value = '0%';
        }
    });
}

function aplicarPrecargaMedico(data) {
    if (!data) return;
    
    // 1. Resumen de actividad
    if (data.resumen) {
        const r = data.resumen;
        if (document.getElementById('med_consultas_realizadas')) 
            document.getElementById('med_consultas_realizadas').value = r.consultas_realizadas || 0;
        if (document.getElementById('med_pacientes_atendidas')) 
            document.getElementById('med_pacientes_atendidas').value = r.pacientes_atendidas || 0;
        if (document.getElementById('med_pacientes_con_signos_alarma')) 
            document.getElementById('med_pacientes_con_signos_alarma').value = r.pacientes_con_signos_alarma || 0;
    }
    
    // 2. Pacientes Atendidas
    if (data.pacientes && Array.isArray(data.pacientes)) {
        const tbody = document.getElementById('pacientesMedicoBody');
        if (tbody) {
            tbody.innerHTML = '';
            data.pacientes.forEach(p => {
                const row = document.createElement('tr');
                
                const nombre = p.nombre_completo || p.nombre || '';
                const semanas = p.semanas_gestacion || p.sdg || '';
                const riesgo = (p.nivel_riesgo || p.riesgo || '').toLowerCase();
                const riesgoObst = p.riesgo_obstetrico || '';
                const consultas = p.consultas_otorgadas || p.consultas || 0;
                const ultimaConsulta = p.ultima_consulta_fecha || p.ultima_atencion || '';
                const diagnostico = p.diagnostico || '';
                const tratamiento = p.tratamiento || '';
                const cumplidas = p.citas_cumplidas === true;

                row.innerHTML = `
                    <td><input type="text" value="${nombre}" class="med-nombre" placeholder="Nombre"></td>
                    <td><input type="number" value="${semanas}" class="med-semanas" placeholder="Sem." min="0"></td>
                    <td>
                        <select class="med-riesgo">
                            <option value="">Seleccionar</option>
                            <option value="bajo" ${riesgo === 'bajo' ? 'selected' : ''}>Bajo</option>
                            <option value="medio" ${riesgo === 'medio' ? 'selected' : ''}>Medio</option>
                            <option value="alto" ${riesgo === 'alto' ? 'selected' : ''}>Alto</option>
                        </select>
                    </td>
                    <td><input type="text" value="${riesgoObst}" class="med-riesgo-obs" placeholder="Riesgo obst."></td>
                    <td><input type="number" value="${consultas}" class="med-consultas" placeholder="#" min="0"></td>
                    <td><input type="date" value="${ultimaConsulta}" class="med-ultima"></td>
                    <td><input type="text" value="${diagnostico}" class="med-diagnostico" placeholder="Diagnóstico"></td>
                    <td><input type="text" value="${tratamiento}" class="med-tratamiento" placeholder="Tratamiento"></td>
                    <td><input type="checkbox" class="med-cumplidas" style="width: auto;" ${cumplidas ? 'checked' : ''}></td>
                    <td><button type="button" class="btn-remove-row" onclick="this.closest('tr').remove(); actualizarJsonPreview();">×</button></td>
                `;
                tbody.appendChild(row);
                row.querySelectorAll('input, select').forEach(el => el.addEventListener('input', actualizarJsonPreview));
            });
        }
    }
    
    showToast('Datos de actividad y pacientes precargados', 'success');
}

function aplicarPrecargaEnfermera(data) {
    if (!data) return;
    
    // 1. Resumen de pacientes y citas
    if (data.resumen) {
        const r = data.resumen;
        if (document.getElementById('enf_total_pacientes_activas')) 
            document.getElementById('enf_total_pacientes_activas').value = r.total_pacientes_activas || 0;
        if (document.getElementById('enf_pacientes_nuevas')) 
            document.getElementById('enf_pacientes_nuevas').value = r.pacientes_nuevas || 0;
        
        calcularEnfermeraSeguimiento();
        
        if (document.getElementById('enf_citas_programadas')) 
            document.getElementById('enf_citas_programadas').value = r.citas_programadas || 0;
        if (document.getElementById('enf_citas_cumplidas')) 
            document.getElementById('enf_citas_cumplidas').value = r.citas_cumplidas || 0;
        if (document.getElementById('enf_citas_canceladas')) 
            document.getElementById('enf_citas_canceladas').value = r.citas_canceladas || 0;
        if (document.getElementById('enf_inasistencias')) 
            document.getElementById('enf_inasistencias').value = r.inasistencias || 0;
    }
    
    // 2. Censo Nominal
    if (data.censo && Array.isArray(data.censo)) {
        const tbody = document.getElementById('censoEnfermeraBody');
        if (tbody) {
            tbody.innerHTML = '';
            data.censo.forEach(p => {
                const row = document.createElement('tr');
                // Mapeo de campos según vista_censo_tabla
                const nombre = p.nombre_completo || p.nombre || '';
                const edad = p.edad || '';
                const semanas = p.sdg || p.semanas_gestacion || '';
                const riesgo = (p.riesgo || p.nivel_riesgo || '').toLowerCase();
                const ultimaAtencion = p.fecha_ultima_atencion || p.ultima_atencion || '';

                row.innerHTML = `
                    <td><input type="text" value="${nombre}" placeholder="Nombre completo"></td>
                    <td><input type="number" value="${edad}" placeholder="Edad" min="0"></td>
                    <td><input type="number" value="${semanas}" placeholder="Semanas" min="0"></td>
                    <td>
                        <select>
                            <option value="">Seleccionar</option>
                            <option value="bajo" ${riesgo === 'bajo' ? 'selected' : ''}>Bajo</option>
                            <option value="medio" ${riesgo === 'medio' ? 'selected' : ''}>Medio</option>
                            <option value="alto" ${riesgo === 'alto' ? 'selected' : ''}>Alto</option>
                        </select>
                    </td>
                    <td><input type="date" value="${ultimaAtencion}"></td>
                    <td><button type="button" class="btn-remove-row" onclick="this.closest('tr').remove(); actualizarJsonPreview();">×</button></td>
                `;
                tbody.appendChild(row);
            });
        }
    }
    
    showToast('Datos del censo y resumen precargados', 'success');
}

function aplicarPrecargaDirector(data) {
    if (document.getElementById('dir_total_pacientes_activas')) 
        document.getElementById('dir_total_pacientes_activas').value = data.total_pacientes_activas || 0;
    if (document.getElementById('dir_consultas_mes')) 
        document.getElementById('dir_consultas_mes').value = data.consultas_mes || 0;
    if (document.getElementById('dir_tasa_asistencia')) 
        document.getElementById('dir_tasa_asistencia').value = data.tasa_asistencia || 0;
    if (document.getElementById('dir_pacientes_alto_riesgo')) 
        document.getElementById('dir_pacientes_alto_riesgo').value = data.pacientes_alto_riesgo || 0;

    if (document.getElementById('dir_consultas_mes_anterior')) 
        document.getElementById('dir_consultas_mes_anterior').value = data.consultas_mes_anterior || 0;
    if (document.getElementById('dir_tasa_asistencia_anterior')) 
        document.getElementById('dir_tasa_asistencia_anterior').value = data.tasa_asistencia_anterior || 0;
    if (document.getElementById('dir_pacientes_alto_riesgo_anterior')) 
        document.getElementById('dir_pacientes_alto_riesgo_anterior').value = data.pacientes_alto_riesgo_anterior || 0;

    if (document.getElementById('dir_riesgo_bajo')) 
        document.getElementById('dir_riesgo_bajo').value = data.riesgo_bajo || 0;
    if (document.getElementById('dir_riesgo_medio')) 
        document.getElementById('dir_riesgo_medio').value = data.riesgo_medio || 0;
    if (document.getElementById('dir_riesgo_alto')) 
        document.getElementById('dir_riesgo_alto').value = data.riesgo_alto || 0;

    if (document.getElementById('dir_medico_consultas_realizadas')) 
        document.getElementById('dir_medico_consultas_realizadas').value = data.medico_consultas_realizadas || 0;
    if (document.getElementById('dir_medico_pacientes_con_signos_alarma')) 
        document.getElementById('dir_medico_pacientes_con_signos_alarma').value = data.medico_pacientes_con_signos_alarma || 0;
    if (document.getElementById('dir_enfermera_pacientes_nuevas')) 
        document.getElementById('dir_enfermera_pacientes_nuevas').value = data.enfermera_pacientes_nuevas || 0;
    if (document.getElementById('dir_ts_inasistencias')) 
        document.getElementById('dir_ts_inasistencias').value = data.ts_inasistencias || 0;
    if (document.getElementById('dir_ts_pacientes_reintegradas')) 
        document.getElementById('dir_ts_pacientes_reintegradas').value = data.ts_pacientes_reintegradas || 0;

    showToast('Datos de vista precargados automáticamente', 'success');
}

function agregarFilaCensoEnfermera() {
    const tbody = document.getElementById('censoEnfermeraBody');
    const row = document.createElement('tr');
    row.innerHTML = `
        <td><input type="text" placeholder="Nombre completo"></td>
        <td><input type="number" placeholder="Edad" min="0"></td>
        <td><input type="number" placeholder="Semanas" min="0"></td>
        <td>
            <select>
                <option value="">Seleccionar</option>
                <option value="bajo">Bajo</option>
                <option value="medio">Medio</option>
                <option value="alto">Alto</option>
            </select>
        </td>
        <td><input type="date"></td>
        <td><button type="button" class="btn-remove-row" onclick="this.closest('tr').remove(); actualizarJsonPreview();">×</button></td>
    `;
    tbody.appendChild(row);
    actualizarJsonPreview();
}

function agregarFilaPacienteMedico() {
    const tbody = document.getElementById('pacientesMedicoBody');
    const row = document.createElement('tr');
    row.innerHTML = `
        <td><input type="text" placeholder="Nombre" class="med-nombre"></td>
        <td><input type="number" placeholder="Sem." min="0" class="med-semanas"></td>
        <td>
            <select class="med-riesgo">
                <option value="">Seleccionar</option>
                <option value="bajo">Bajo</option>
                <option value="medio">Medio</option>
                <option value="alto">Alto</option>
            </select>
        </td>
        <td><input type="text" placeholder="Riesgo obst." class="med-riesgo-obs"></td>
        <td><input type="number" placeholder="#" min="0" class="med-consultas"></td>
        <td><input type="date" class="med-ultima"></td>
        <td><input type="text" placeholder="Diagnóstico" class="med-diagnostico"></td>
        <td><input type="text" placeholder="Tratamiento" class="med-tratamiento"></td>
        <td><input type="checkbox" class="med-cumplidas" style="width: auto;"></td>
        <td><button type="button" class="btn-remove-row" onclick="this.closest('tr').remove(); actualizarJsonPreview();">×</button></td>
    `;
    tbody.appendChild(row);
    row.querySelectorAll('input, select').forEach(el => el.addEventListener('input', actualizarJsonPreview));
    actualizarJsonPreview();
}

function agregarFilaCasoTS() {
    const tbody = document.getElementById('casosTSBody');
    const row = document.createElement('tr');
    row.innerHTML = `
        <td><input type="text" placeholder="Nombre"></td>
        <td><input type="tel" placeholder="Teléfono"></td>
        <td><input type="date"></td>
        <td><input type="text" placeholder="Motivo"></td>
        <td><input type="checkbox" style="width: auto;"></td>
        <td>
            <select>
                <option value="">Seleccionar</option>
                <option value="pendiente">Pendiente</option>
                <option value="reintegrada">Reintegrada</option>
                <option value="sin_contacto">Sin Contacto</option>
            </select>
        </td>
        <td><input type="text" placeholder="Mensaje"></td>
        <td><button type="button" class="btn-remove-row" onclick="this.closest('tr').remove(); actualizarJsonPreview();">×</button></td>
    `;
    tbody.appendChild(row);
    row.querySelectorAll('input, select').forEach(el => el.addEventListener('input', actualizarJsonPreview));
    actualizarJsonPreview();
}

function agregarAlerta() {
    const input = document.getElementById('dir_nueva_alerta');
    const texto = input.value.trim();
    if (!texto) return;
    
    alertas.push(texto);
    input.value = '';
    renderAlertas();
    actualizarJsonPreview();
}

function renderAlertas() {
    const container = document.getElementById('listaAlertas');
    if (!container) return;
    container.innerHTML = alertas.map((alerta, i) => `
        <div class="alerta-item">
            <span>${alerta}</span>
            <button type="button" class="btn-remove-row" onclick="eliminarAlerta(${i})">×</button>
        </div>
    `).join('');
}

function eliminarAlerta(index) {
    alertas.splice(index, 1);
    renderAlertas();
    actualizarJsonPreview();
}

function calcularEnfermeraSeguimiento() {
    const activas = parseInt(document.getElementById('enf_total_pacientes_activas').value) || 0;
    const nuevas = parseInt(document.getElementById('enf_pacientes_nuevas').value) || 0;
    document.getElementById('enf_pacientes_en_seguimiento').value = Math.max(0, activas - nuevas);
    actualizarJsonPreview();
}

function calcularTSInjustificadas() {
    const total = parseInt(document.getElementById('ts_total_inasistencias').value) || 0;
    const justificadas = parseInt(document.getElementById('ts_justificadas').value) || 0;
    document.getElementById('ts_sin_justificacion').value = Math.max(0, total - justificadas);
    actualizarJsonPreview();
}

function buildReporteData(rol) {
    switch(rol) {
        case 'enfermera':
            return {
                resumen: {
                    total_pacientes_activas: parseInt(document.getElementById('enf_total_pacientes_activas').value) || 0,
                    pacientes_nuevas: parseInt(document.getElementById('enf_pacientes_nuevas').value) || 0,
                    pacientes_en_seguimiento: parseInt(document.getElementById('enf_pacientes_en_seguimiento').value) || 0,
                    citas_programadas: parseInt(document.getElementById('enf_citas_programadas').value) || 0,
                    citas_cumplidas: parseInt(document.getElementById('enf_citas_cumplidas').value) || 0,
                    citas_canceladas: parseInt(document.getElementById('enf_citas_canceladas').value) || 0,
                    inasistencias: parseInt(document.getElementById('enf_inasistencias').value) || 0
                },
                censo: Array.from(document.getElementById('censoEnfermeraBody').rows).map(row => ({
                    nombre: row.cells[0].querySelector('input').value,
                    edad: parseInt(row.cells[1].querySelector('input').value) || 0,
                    semanas_gestacion: parseInt(row.cells[2].querySelector('input').value) || 0,
                    nivel_riesgo: row.cells[3].querySelector('select').value,
                    fecha_ultima_atencion: row.cells[4].querySelector('input').value
                })),
                semana_epidemiologica: parseInt(document.getElementById('enf_semana_epidemiologica').value) || 0,
                generado_automaticamente: document.getElementById('enf_generado_automaticamente').checked
            };
        
        case 'medico':
            return {
                resumen: {
                    consultas_realizadas: parseInt(document.getElementById('med_consultas_realizadas').value) || 0,
                    pacientes_atendidas: parseInt(document.getElementById('med_pacientes_atendidas').value) || 0,
                    pacientes_con_signos_alarma: parseInt(document.getElementById('med_pacientes_con_signos_alarma').value) || 0
                },
                pacientes: Array.from(document.getElementById('pacientesMedicoBody').rows).map(row => ({
                    nombre: row.querySelector('.med-nombre').value,
                    semanas_gestacion: parseInt(row.querySelector('.med-semanas').value) || 0,
                    nivel_riesgo: row.querySelector('.med-riesgo').value,
                    riesgo_obstetrico: row.querySelector('.med-riesgo-obs').value,
                    consultas_otorgadas: parseInt(row.querySelector('.med-consultas').value) || 0,
                    ultima_consulta_fecha: row.querySelector('.med-ultima').value,
                    diagnostico: row.querySelector('.med-diagnostico').value,
                    tratamiento: row.querySelector('.med-tratamiento').value,
                    citas_cumplidas: row.querySelector('.med-cumplidas').checked
                })),
                observaciones_generales: document.getElementById('med_observaciones_generales').value
            };
        
        case 'trabajo_social':
            return {
                resumen: {
                    total_inasistencias: parseInt(document.getElementById('ts_total_inasistencias').value) || 0,
                    justificadas: parseInt(document.getElementById('ts_justificadas').value) || 0,
                    sin_justificacion: parseInt(document.getElementById('ts_sin_justificacion').value) || 0,
                    pacientes_reintegradas: parseInt(document.getElementById('ts_pacientes_reintegradas').value) || 0
                },
                casos: Array.from(document.getElementById('casosTSBody').rows).map(row => ({
                    nombre: row.cells[0].querySelector('input').value,
                    telefono: row.cells[1].querySelector('input').value,
                    fecha_cita: row.cells[2].querySelector('input').value,
                    motivo: row.cells[3].querySelector('input').value,
                    justificada: row.cells[4].querySelector('input').checked,
                    observacion_ts: row.cells[5].querySelector('select').value,
                    mensaje_seguimiento: row.cells[6].querySelector('input').value
                })),
                notas_adicionales: document.getElementById('ts_notas_adicionales').value
            };
        
        case 'director_general':
            return {
                kpis: {
                    total_pacientes_activas: parseInt(document.getElementById('dir_total_pacientes_activas').value) || 0,
                    consultas_mes: parseInt(document.getElementById('dir_consultas_mes').value) || 0,
                    tasa_asistencia: parseFloat(document.getElementById('dir_tasa_asistencia').value) || 0,
                    pacientes_alto_riesgo: parseInt(document.getElementById('dir_pacientes_alto_riesgo').value) || 0
                },
                comparativo: {
                    total_pacientes_activas_anterior: parseInt(document.getElementById('dir_total_pacientes_activas_anterior').value) || 0,
                    consultas_mes_anterior: parseInt(document.getElementById('dir_consultas_mes_anterior').value) || 0,
                    tasa_asistencia_anterior: parseFloat(document.getElementById('dir_tasa_asistencia_anterior').value) || 0,
                    pacientes_alto_riesgo_anterior: parseInt(document.getElementById('dir_pacientes_alto_riesgo_anterior').value) || 0,
                    variacion_pacientes: document.getElementById('dir_variacion_pacientes').value,
                    variacion_consultas: document.getElementById('dir_variacion_consultas').value,
                    variacion_asistencia: document.getElementById('dir_variacion_asistencia').value
                },
                distribucion_riesgo: {
                    bajo: parseInt(document.getElementById('dir_riesgo_bajo').value) || 0,
                    medio: parseInt(document.getElementById('dir_riesgo_medio').value) || 0,
                    alto: parseInt(document.getElementById('dir_riesgo_alto').value) || 0
                },
                resumen_por_area: {
                    medico: {
                        consultas_realizadas: parseInt(document.getElementById('dir_medico_consultas_realizadas').value) || 0,
                        pacientes_con_signos_alarma: parseInt(document.getElementById('dir_medico_pacientes_con_signos_alarma').value) || 0
                    },
                    enfermera: {
                        pacientes_nuevas: parseInt(document.getElementById('dir_enfermera_pacientes_nuevas').value) || 0,
                        censo_actualizado: document.getElementById('dir_enfermera_censo_actualizado').checked
                    },
                    trabajo_social: {
                        inasistencias: parseInt(document.getElementById('dir_ts_inasistencias').value) || 0,
                        pacientes_reintegradas: parseInt(document.getElementById('dir_ts_pacientes_reintegradas').value) || 0
                    }
                },
                alertas: alertas
            };
        
        default:
            return {};
    }
}

function getTipoPorRol(rol) {
    const tipos = {
        'enfermera': 'censo_mensual',
        'medico': 'seguimiento_clinico',
        'trabajo_social': 'analisis_inasistencias',
        'director_general': 'reporte_direccion'
    };
    return tipos[rol] || 'desconocido';
}

function getPeriodoPorRol(rol) {
    const prefix = rol === 'director_general' ? 'dir' : (rol === 'trabajo_social' ? 'ts' : rol.substring(0, 3));
    const inicio = document.getElementById(`${prefix}_periodo_inicio`)?.value || '';
    const fin = document.getElementById(`${prefix}_periodo_fin`)?.value || '';
    return { inicio, fin };
}

function buildPayload(rol, estado) {
    const { inicio, fin } = getPeriodoPorRol(rol);
    let parsedUserId = null;
    if (typeof USER_ID !== 'undefined' && USER_ID && USER_ID !== 'None') {
        parsedUserId = parseInt(USER_ID);
    }
    
    return {
        id_usuario: parsedUserId,
        periodo_inicio: inicio || null,
        periodo_fin: fin || null,
        generado_por: rol,
        tipo: getTipoPorRol(rol),
        estado: estado,
        datos: buildReporteData(rol)
    };
}

function syntaxHighlight(json) {
    if (typeof json !== 'string') {
        json = JSON.stringify(json, null, 2);
    }
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        let cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

function actualizarJsonPreview() {
    return;
}

async function guardarBorrador() {
    if (typeof USER_ROL === 'undefined' || !USER_ROL) return;
    
    const payload = buildPayload(USER_ROL, 'borrador');
    
    try {
        let response;
        if (currentReporteId) {
            response = await fetch(`/gestion/api/reportes/${currentReporteId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ estado: 'borrador', datos: payload.datos })
            });
        } else {
            response = await fetch('/gestion/api/reportes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error al guardar borrador');
        }
        
        if (data.id_reporte) currentReporteId = data.id_reporte;
        
        showToast('Borrador guardado correctamente', 'success');
        cargarReportesAnteriores();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function generarReporte() {
    if (typeof USER_ROL === 'undefined' || !USER_ROL) return;
    
    if (!validarFormulario(USER_ROL)) return;
    
    const payload = buildPayload(USER_ROL, 'generado');
    
    try {
        let response;
        if (currentReporteId) {
            response = await fetch(`/gestion/api/reportes/${currentReporteId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ estado: 'generado', datos: payload.datos })
            });
        } else {
            response = await fetch('/gestion/api/reportes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error al generar reporte');
        }
        
        if (data.id_reporte) currentReporteId = data.id_reporte;
        
        showToast('Reporte generado exitosamente', 'success');
        deshabilitarFormulario();
        cargarReportesAnteriores();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function validarFormulario(rol) {
    const { inicio, fin } = getPeriodoPorRol(rol);
    
    if (!inicio || !fin) {
        showToast('Por favor completa las fechas del período', 'error');
        return false;
    }
    
    const requiredFields = {
        'enfermera': ['enf_total_pacientes_activas', 'enf_pacientes_nuevas', 'enf_citas_programadas', 'enf_citas_cumplidas', 'enf_citas_canceladas', 'enf_inasistencias'],
        'medico': ['med_consultas_realizadas', 'med_pacientes_atendidas', 'med_pacientes_con_signos_alarma'],
        'trabajo_social': ['ts_total_inasistencias', 'ts_justificadas', 'ts_pacientes_reintegradas'],
        'director_general': ['dir_total_pacientes_activas', 'dir_consultas_mes', 'dir_tasa_asistencia', 'dir_pacientes_alto_riesgo']
    };
    
    const fields = requiredFields[rol] || [];
    for (const fieldId of fields) {
        const el = document.getElementById(fieldId);
        if (el && !el.value) {
            showToast(`Por favor completa el campo: ${el.previousElementSibling?.textContent || fieldId}`, 'error');
            el.focus();
            return false;
        }
    }
    
    return true;
}

function deshabilitarFormulario() {
    if (typeof USER_ROL === 'undefined' || !USER_ROL) return;
    const formId = {
        'enfermera': 'formularioEnfermera',
        'medico': 'formularioMedico',
        'trabajo_social': 'formularioTrabajoSocial',
        'director_general': 'formularioDirector'
    }[USER_ROL];
    
    if (formId) {
        const formEl = document.getElementById(formId);
        if (formEl) {
            formEl.querySelectorAll('input, select, textarea, button').forEach(el => {
                el.disabled = true;
            });
        }
    }
}

async function cargarBorradorActual() {
    if (typeof USER_ROL === 'undefined' || !USER_ROL) return;
    
    try {
        const response = await fetch(`/gestion/api/reportes?generado_por=${USER_ROL}&estado=borrador`);
        
        if (response.ok) {
            const data = await response.json();
            if (data.data && data.data.length > 0) {
                currentReporteId = data.data[0].id_reporte;
                preLlenarFormulario(data.data[0]);
            }
        }
    } catch (error) {
        console.log('No se encontró borrador');
    }
}

async function cargarReportesAnteriores() {
    if (typeof USER_ROL === 'undefined' || !USER_ROL) return;
    
    const tbody = document.getElementById('tablaReportesAnteriores');
    if (!tbody) return;
    
    try {
        const response = await fetch(`/gestion/api/reportes?generado_por=${USER_ROL}`);
        
        if (!response.ok) throw new Error('Error al cargar reportes');
        
        const data = await response.json();
        const reportes = data.data || [];

        if (reportes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--gray-400); padding: 2rem;">No hay reportes anteriores</td></tr>';
            return;
        }
        
        tbody.innerHTML = reportes.map(r => {
            const estadoClase = {
                'borrador': 'badge-gray',
                'generado': 'badge-info',
                'enviado': 'badge-success',
                'archivado': 'badge-warning'
            }[r.datos?.estado] || 'badge-gray';
            
            let fechaFormateada = '-';
            if (r.fecha) {
                fechaFormateada = r.fecha.split('T')[0];
            }
            
            return `
                <tr>
                    <td><strong>${(r.tipo || 'desconocido').replace('_', ' ')}</strong></td>
                    <td>${r.periodo_inicio || 'N/A'} - ${r.periodo_fin || 'N/A'}</td>
                    <td><span class="badge ${estadoClase}">${r.datos?.estado || 'desconocido'}</span></td>
                    <td>${fechaFormateada}</td>
                    <td>
                        <div style="display: flex; gap: 0.5rem;">
                            <button class="btn btn-secondary btn-icon" title="Ver" onclick="verReporte(${r.id_reporte})">
                                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                            </button>
                            <button class="btn btn-success btn-icon" title="Descargar" onclick="descargarReporteId(${r.id_reporte})">
                                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--red); padding: 2rem;">Error al cargar reportes</td></tr>';
    }
}

async function verReporte(id) {
    try {
        const response = await fetch(`/gestion/api/reportes/${id}`);
        
        if (!response.ok) throw new Error('Error al cargar reporte');
        
        const data = await response.json();
        currentReporteJson = data;
        
        document.getElementById('modalJson').style.display = 'flex';
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function descargarReporte() {
    if (!currentReporteJson) return;
    const id = currentReporteJson.id_reporte;
    window.location.href = `/gestion/api/reportes/${id}/descargar`;
}

function descargarReporteId(id) {
    window.location.href = `/gestion/api/reportes/${id}/descargar`;
}

function descargarJsonActual() {
    if (!currentReporteJson) return;
    descargarJson(currentReporteJson, `reporte_${currentReporteJson.tipo}_${currentReporteJson.periodo_inicio}.json`);
}

function descargarJson(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function closeJsonModal() {
    document.getElementById('modalJson').style.display = 'none';
    currentReporteJson = null;
}

function preLlenarFormulario(reporte) {
    const rol = reporte.generado_por;
    
    const prefix = rol === 'director_general' ? 'dir' : rol.substring(0, 3);
    const inicioEl = document.getElementById(`${prefix}_periodo_inicio`);
    const finEl = document.getElementById(`${prefix}_periodo_fin`);
    if (inicioEl) inicioEl.value = reporte.periodo_inicio || '';
    if (finEl) finEl.value = reporte.periodo_fin || '';

    const d = reporte.datos;
    if (!d) return;

    if (rol === 'enfermera') {
        if (d.resumen) {
            document.getElementById('enf_total_pacientes_activas').value = d.resumen.total_pacientes_activas || '';
            document.getElementById('enf_pacientes_nuevas').value = d.resumen.pacientes_nuevas || '';
            calcularEnfermeraSeguimiento();
            document.getElementById('enf_citas_programadas').value = d.resumen.citas_programadas || '';
            document.getElementById('enf_citas_cumplidas').value = d.resumen.citas_cumplidas || '';
            document.getElementById('enf_citas_canceladas').value = d.resumen.citas_canceladas || '';
            document.getElementById('enf_inasistencias').value = d.resumen.inasistencias || '';
        }
        if (d.semana_epidemiologica) document.getElementById('enf_semana_epidemiologica').value = d.semana_epidemiologica;
        if (d.generado_automaticamente !== undefined) document.getElementById('enf_generado_automaticamente').checked = d.generado_automaticamente;
        
        if (d.censo && Array.isArray(d.censo) && d.censo.length > 0) {
            const tbody = document.getElementById('censoEnfermeraBody');
            tbody.innerHTML = '';
            d.censo.forEach(p => {
                const row = document.createElement('tr');
                const nombre = p.nombre_completo || p.nombre || '';
                const edad = p.edad || '';
                const semanas = p.sdg || p.semanas_gestacion || '';
                const riesgo = (p.riesgo || p.nivel_riesgo || '').toLowerCase();
                const ultimaAtencion = p.fecha_ultima_atencion || p.ultima_atencion || '';

                row.innerHTML = `
                    <td><input type="text" value="${nombre}" placeholder="Nombre completo"></td>
                    <td><input type="number" value="${edad}" placeholder="Edad" min="0"></td>
                    <td><input type="number" value="${semanas}" placeholder="Semanas" min="0"></td>
                    <td>
                        <select>
                            <option value="">Seleccionar</option>
                            <option value="bajo" ${riesgo === 'bajo' ? 'selected' : ''}>Bajo</option>
                            <option value="medio" ${riesgo === 'medio' ? 'selected' : ''}>Medio</option>
                            <option value="alto" ${riesgo === 'alto' ? 'selected' : ''}>Alto</option>
                        </select>
                    </td>
                    <td><input type="date" value="${ultimaAtencion}"></td>
                    <td><button type="button" class="btn-remove-row" onclick="this.closest('tr').remove(); actualizarJsonPreview();">×</button></td>
                `;
                tbody.appendChild(row);
                row.querySelectorAll('input, select').forEach(el => el.addEventListener('input', actualizarJsonPreview));
            });
        }
    } else if (rol === 'medico') {
        if (d.resumen) {
            document.getElementById('med_consultas_realizadas').value = d.resumen.consultas_realizadas || '';
            document.getElementById('med_pacientes_atendidas').value = d.resumen.pacientes_atendidas || '';
            document.getElementById('med_pacientes_con_signos_alarma').value = d.resumen.pacientes_con_signos_alarma || '';
        }
        if (d.observaciones_generales) document.getElementById('med_observaciones_generales').value = d.observaciones_generales;
        
        if (d.pacientes && Array.isArray(d.pacientes) && d.pacientes.length > 0) {
            const tbody = document.getElementById('pacientesMedicoBody');
            tbody.innerHTML = '';
            d.pacientes.forEach(p => {
                const row = document.createElement('tr');
                const nombre = p.nombre_completo || p.nombre || '';
                const semanas = p.semanas_gestacion || p.sdg || '';
                const riesgo = (p.nivel_riesgo || p.riesgo || '').toLowerCase();
                const riesgoObst = p.riesgo_obstetrico || '';
                const consultas = p.consultas_otorgadas || p.consultas || 0;
                const ultimaConsulta = p.ultima_consulta_fecha || p.ultima_atencion || '';
                const diagnostico = p.diagnostico || '';
                const tratamiento = p.tratamiento || '';
                const cumplidas = p.citas_cumplidas === true;

                row.innerHTML = `
                    <td><input type="text" class="med-nombre" value="${nombre}"></td>
                    <td><input type="number" class="med-semanas" value="${semanas}"></td>
                    <td>
                        <select class="med-riesgo">
                            <option value="">Seleccionar</option>
                            <option value="bajo" ${riesgo === 'bajo' ? 'selected' : ''}>Bajo</option>
                            <option value="medio" ${riesgo === 'medio' ? 'selected' : ''}>Medio</option>
                            <option value="alto" ${riesgo === 'alto' ? 'selected' : ''}>Alto</option>
                        </select>
                    </td>
                    <td><input type="text" class="med-riesgo-obs" value="${riesgoObst}"></td>
                    <td><input type="number" class="med-consultas" value="${consultas}"></td>
                    <td><input type="date" class="med-ultima" value="${ultimaConsulta}"></td>
                    <td><input type="text" class="med-diagnostico" value="${diagnostico}"></td>
                    <td><input type="text" class="med-tratamiento" value="${tratamiento}"></td>
                    <td><input type="checkbox" class="med-cumplidas" style="width: auto;" ${cumplidas ? 'checked' : ''}></td>
                    <td><button type="button" class="btn-remove-row" onclick="this.closest('tr').remove(); actualizarJsonPreview();">×</button></td>
                `;
                tbody.appendChild(row);
                row.querySelectorAll('input, select').forEach(el => el.addEventListener('input', actualizarJsonPreview));
            });
        }
    } else if (rol === 'trabajo_social') {
        if (d.resumen) {
            document.getElementById('ts_total_inasistencias').value = d.resumen.total_inasistencias || '';
            document.getElementById('ts_justificadas').value = d.resumen.justificadas || '';
            calcularTSInjustificadas();
            document.getElementById('ts_pacientes_reintegradas').value = d.resumen.pacientes_reintegradas || '';
        }
        if (d.notas_adicionales) document.getElementById('ts_notas_adicionales').value = d.notas_adicionales;
        
        if (d.casos && Array.isArray(d.casos) && d.casos.length > 0) {
            const tbody = document.getElementById('casosTSBody');
            tbody.innerHTML = '';
            d.casos.forEach(c => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><input type="text" value="${c.nombre || ''}"></td>
                    <td><input type="tel" value="${c.telefono || ''}"></td>
                    <td><input type="date" value="${c.fecha_cita || ''}"></td>
                    <td><input type="text" value="${c.motivo || ''}"></td>
                    <td><input type="checkbox" style="width: auto;" ${c.justificada ? 'checked' : ''}></td>
                    <td>
                        <select>
                            <option value="">Seleccionar</option>
                            <option value="pendiente" ${c.observacion_ts === 'pendiente' ? 'selected' : ''}>Pendiente</option>
                            <option value="reintegrada" ${c.observacion_ts === 'reintegrada' ? 'selected' : ''}>Reintegrada</option>
                            <option value="sin_contacto" ${c.observacion_ts === 'sin_contacto' ? 'selected' : ''}>Sin Contacto</option>
                        </select>
                    </td>
                    <td><input type="text" value="${c.mensaje_seguimiento || ''}"></td>
                    <td><button type="button" class="btn-remove-row" onclick="this.closest('tr').remove(); actualizarJsonPreview();">×</button></td>
                `;
                tbody.appendChild(row);
            });
        }
    } else if (rol === 'director_general') {
        if (d.kpis) {
            document.getElementById('dir_total_pacientes_activas').value = d.kpis.total_pacientes_activas || '';
            document.getElementById('dir_consultas_mes').value = d.kpis.consultas_mes || '';
            document.getElementById('dir_tasa_asistencia').value = d.kpis.tasa_asistencia || '';
            document.getElementById('dir_pacientes_alto_riesgo').value = d.kpis.pacientes_alto_riesgo || '';
        }
        if (d.comparativo) {
            document.getElementById('dir_total_pacientes_activas_anterior').value = d.comparativo.total_pacientes_activas_anterior || '';
            document.getElementById('dir_consultas_mes_anterior').value = d.comparativo.consultas_mes_anterior || '';
            document.getElementById('dir_tasa_asistencia_anterior').value = d.comparativo.tasa_asistencia_anterior || '';
            document.getElementById('dir_pacientes_alto_riesgo_anterior').value = d.comparativo.pacientes_alto_riesgo_anterior || '';
            document.getElementById('dir_variacion_pacientes').value = d.comparativo.variacion_pacientes || '';
            document.getElementById('dir_variacion_consultas').value = d.comparativo.variacion_consultas || '';
            document.getElementById('dir_variacion_asistencia').value = d.comparativo.variacion_asistencia || '';
        }
        if (d.distribucion_riesgo) {
            document.getElementById('dir_riesgo_bajo').value = d.distribucion_riesgo.bajo || '';
            document.getElementById('dir_riesgo_medio').value = d.distribucion_riesgo.medio || '';
            document.getElementById('dir_riesgo_alto').value = d.distribucion_riesgo.alto || '';
        }
        if (d.resumen_por_area) {
            if (d.resumen_por_area.medico) {
                document.getElementById('dir_medico_consultas_realizadas').value = d.resumen_por_area.medico.consultas_realizadas || '';
                document.getElementById('dir_medico_pacientes_con_signos_alarma').value = d.resumen_por_area.medico.pacientes_con_signos_alarma || '';
            }
            if (d.resumen_por_area.enfermera) {
                document.getElementById('dir_enfermera_pacientes_nuevas').value = d.resumen_por_area.enfermera.pacientes_nuevas || '';
                document.getElementById('dir_enfermera_censo_actualizado').checked = d.resumen_por_area.enfermera.censo_actualizado || false;
            }
            if (d.resumen_por_area.trabajo_social) {
                document.getElementById('dir_ts_inasistencias').value = d.resumen_por_area.trabajo_social.inasistencias || '';
                document.getElementById('dir_ts_pacientes_reintegradas').value = d.resumen_por_area.trabajo_social.pacientes_reintegradas || '';
            }
        }
        if (d.alertas) {
            alertas = d.alertas;
            renderAlertas();
        }
    }
    
    actualizarJsonPreview();
}

function showToast(message, type) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            ${type === 'success' ? '<polyline points="20 6 9 17 4 12"></polyline>' : '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>'}
        </svg>
        ${message}
    `;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function showConfirmModal(title, message, callback) {
    const modalTitle = document.getElementById('modalConfirmTitle');
    const modalMsg = document.getElementById('modalConfirmMessage');
    const modal = document.getElementById('modalConfirm');
    const modalBtn = document.getElementById('modalConfirmBtn');

    if (modalTitle) modalTitle.textContent = title;
    if (modalMsg) modalMsg.textContent = message;
    if (modal) modal.classList.add('open');
    if (modalBtn) {
        modalBtn.onclick = () => {
            closeConfirmModal();
            callback();
        };
    }
}

function closeConfirmModal() {
    const modal = document.getElementById('modalConfirm');
    if (modal) modal.classList.remove('open');
}

function limpiarFormulario() {
    if (typeof USER_ROL === 'undefined' || !USER_ROL) return;
    const formId = {
        'enfermera': 'formularioEnfermera',
        'medico': 'formularioMedico',
        'trabajo_social': 'formularioTrabajoSocial',
        'director_general': 'formularioDirector'
    }[USER_ROL];
    
    if (formId) {
        const formEl = document.getElementById(formId);
        if (formEl) {
            formEl.querySelectorAll('input:not([type="checkbox"]), textarea').forEach(el => el.value = '');
            formEl.querySelectorAll('input[type="checkbox"]').forEach(el => el.checked = false);
            formEl.querySelectorAll('select').forEach(el => el.selectedIndex = 0);
        }
    }
    
    const censoBody = document.getElementById('censoEnfermeraBody');
    if (censoBody) censoBody.innerHTML = '';
    const pacientesBody = document.getElementById('pacientesMedicoBody');
    if (pacientesBody) pacientesBody.innerHTML = '';
    const casosBody = document.getElementById('casosTSBody');
    if (casosBody) casosBody.innerHTML = '';
    
    alertas = [];
    renderAlertas();
    
    currentReporteId = null;
    showToast('Formulario limpiado', 'success');
    actualizarJsonPreview();
}

function toggleCollapsible(id) {
    const el = document.getElementById(id);
    if (el) el.classList.toggle('open');
}

document.addEventListener('DOMContentLoaded', () => {
    if (typeof USER_ROL !== 'undefined' && USER_ROL) {
        renderFormularioPorRol(USER_ROL);
        cargarBorradorActual();
        cargarReportesAnteriores();
    }
    
    document.querySelectorAll('input, select, textarea').forEach(el => {
        el.addEventListener('input', () => {
            actualizarJsonPreview();
            if (USER_ROL === 'director_general') {
                calcularVariacionesDirector();
            }
        });
    });
    
    document.querySelectorAll('input[type="checkbox"]').forEach(el => {
        el.addEventListener('change', actualizarJsonPreview);
    });
});
