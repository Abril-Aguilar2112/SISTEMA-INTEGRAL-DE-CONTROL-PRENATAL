document.addEventListener('DOMContentLoaded', () => {
    cargarReportes();

    document.getElementById('filtroArea')?.addEventListener('change', cargarReportes);
    document.getElementById('filtroMes')?.addEventListener('change', cargarReportes);
});

async function cargarReportes() {
    const area = document.getElementById('filtroArea')?.value || '';
    const mes = document.getElementById('filtroMes')?.value || '';
    const tbody = document.getElementById('tablaReportes');
    
    if (!tbody) return;
    
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 3rem; color: var(--gray-400);">Cargando reportes...</td></tr>';

    try {
        let url = `/gestion/api/reportes?estado=generado`;
        if (area) url += `&generado_por=${area}`;
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('Error al cargar reportes');
        
        const data = await response.json();
        let reportes = data.data || [];

        if (mes) {
            reportes = reportes.filter(r => r.periodo_inicio.startsWith(mes));
        }

        if (reportes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 3rem; color: var(--gray-400);">No se encontraron reportes generados</td></tr>';
            return;
        }

        tbody.innerHTML = reportes.map(r => renderFilaReporte(r)).join('');
    } catch (error) {
        console.error(error);
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 3rem; color: var(--red);">Error al conectar con el servidor</td></tr>';
    }
}

function renderFilaReporte(r) {
    const rolMap = {
        'enfermera': 'Enfermera',
        'medico': 'Médico',
        'trabajo_social': 'Trabajo Social',
        'director_general': 'Director'
    };

    const d = r.datos || {};
    let resumenHtml = '';

    if (r.generado_por === 'enfermera') {
        resumenHtml = `
            <div class="report-summary-card">
                <div class="summary-item"><span class="summary-label">Activas</span><span class="summary-value">${d.resumen?.total_pacientes_activas || 0}</span></div>
                <div class="summary-item"><span class="summary-label">Nuevas</span><span class="summary-value">${d.resumen?.pacientes_nuevas || 0}</span></div>
                <div class="summary-item"><span class="summary-label">Citas</span><span class="summary-value">${d.resumen?.citas_cumplidas || 0}</span></div>
            </div>
        `;
    } else if (r.generado_por === 'medico') {
        resumenHtml = `
            <div class="report-summary-card">
                <div class="summary-item"><span class="summary-label">Consultas</span><span class="summary-value">${d.resumen?.consultas_realizadas || 0}</span></div>
                <div class="summary-item"><span class="summary-label">Atendidas</span><span class="summary-value">${d.resumen?.pacientes_atendidas || 0}</span></div>
                <div class="summary-item"><span class="summary-label">Alarmas</span><span class="summary-value" style="color: var(--red);">${d.resumen?.pacientes_con_signos_alarma || 0}</span></div>
            </div>
        `;
    } else if (r.generado_por === 'trabajo_social') {
        resumenHtml = `
            <div class="report-summary-card">
                <div class="summary-item"><span class="summary-label">Inasistencias</span><span class="summary-value">${d.resumen?.total_inasistencias || 0}</span></div>
                <div class="summary-item"><span class="summary-label">Reintegradas</span><span class="summary-value">${d.resumen?.pacientes_reintegradas || 0}</span></div>
            </div>
        `;
    } else if (r.generado_por === 'director_general') {
        resumenHtml = `
            <div class="report-summary-card">
                <div class="summary-item"><span class="summary-label">Asistencia</span><span class="summary-value">${d.kpis?.tasa_asistencia || 0}%</span></div>
                <div class="summary-item"><span class="summary-label">Alto Riesgo</span><span class="summary-value">${d.kpis?.pacientes_alto_riesgo || 0}</span></div>
            </div>
        `;
    }

    return `
        <tr>
            <td>
                <div style="font-weight: 600;">${(r.tipo || 'Reporte').replace('_', ' ').toUpperCase()}</div>
                ${resumenHtml}
            </td>
            <td><span class="badge-area badge-${r.generado_por}">${rolMap[r.generado_por] || r.generado_por}</span></td>
            <td>${r.periodo_inicio} - ${r.periodo_fin}</td>
            <td>${r.fecha.split('T')[0]}</td>
            <td>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="btn btn-secondary btn-icon" title="Visualizar" onclick="visualizarReporte(${r.id_reporte})">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    </button>
                    <button class="btn btn-success btn-icon" title="Descargar Excel" onclick="descargarReporteId(${r.id_reporte})">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                    </button>
                </div>
            </td>
        </tr>
    `;
}

async function visualizarReporte(id) {
    const modal = document.getElementById('modalPreview');
    const content = document.getElementById('previewContent');
    if (!modal || !content) return;

    content.innerHTML = '<div style="text-align: center; padding: 2rem;">Cargando detalles...</div>';
    modal.style.display = 'flex';

    try {
        const response = await fetch(`/gestion/api/reportes/${id}`);
        if (!response.ok) throw new Error('Error');
        
        const res = await response.json();
        const r = res.data || res;
        const d = r.datos || {};

        const rolMap = {
            'enfermera': 'Enfermera',
            'medico': 'Médico',
            'trabajo_social': 'Trabajo Social',
            'director_general': 'Director'
        };

        let previewHtml = `
            <div class="preview-section">
                <h4 style="color: var(--gray-500); margin-bottom: 1rem; border-bottom: 2px solid var(--purple-light);">INFORMACIÓN GENERAL</h4>
                <div class="preview-grid">
                    <div class="preview-item"><span class="preview-label">Área:</span><span class="preview-value">${(rolMap[r.generado_por] || r.generado_por || '').toUpperCase()}</span></div>
                    <div class="preview-item"><span class="preview-label">Tipo:</span><span class="preview-value">${(r.tipo || '').replace('_', ' ').toUpperCase()}</span></div>
                    <div class="preview-item"><span class="preview-label">Período:</span><span class="preview-value">${r.periodo_inicio} al ${r.periodo_fin}</span></div>
                    <div class="preview-item"><span class="preview-label">Fecha:</span><span class="preview-value">${(r.fecha || '').split('T')[0]}</span></div>
                </div>
            </div>
        `;

        if (r.generado_por === 'enfermera') {
            previewHtml += renderPreviewEnfermera(d);
        } else if (r.generado_por === 'medico') {
            previewHtml += renderPreviewMedico(d);
        } else if (r.generado_por === 'trabajo_social') {
            previewHtml += renderPreviewTS(d);
        } else if (r.generado_por === 'director_general') {
            previewHtml += renderPreviewDirector(d);
        }

        content.innerHTML = previewHtml;
    } catch (error) {
        content.innerHTML = '<div style="color: var(--red); padding: 2rem;">Error al cargar los detalles del reporte.</div>';
    }
}

function renderPreviewEnfermera(d) {
    const res = d.resumen || {};
    return `
        <div class="preview-section">
            <h4 style="color: var(--gray-500); margin-bottom: 1rem; border-bottom: 2px solid var(--purple-light);">RESUMEN DE PACIENTES</h4>
            <div class="preview-grid">
                <div class="preview-item"><span>Total Activas:</span><span class="preview-value">${res.total_pacientes_activas || 0}</span></div>
                <div class="preview-item"><span>Pacientes Nuevas:</span><span class="preview-value">${res.pacientes_nuevas || 0}</span></div>
                <div class="preview-item"><span>En Seguimiento:</span><span class="preview-value">${res.pacientes_en_seguimiento || 0}</span></div>
                <div class="preview-item"><span>Citas Cumplidas:</span><span class="preview-value">${res.citas_cumplidas || 0}</span></div>
            </div>
        </div>
        ${d.censo ? `
            <div class="preview-section">
                <h4 style="color: var(--gray-500); margin-bottom: 1rem;">MUESTRA DEL CENSO (${d.censo.length} registros)</h4>
                <table style="width: 100%; border-collapse: collapse; font-size: 0.875rem;">
                    <thead><tr style="text-align: left; border-bottom: 1px solid var(--gray-200);"><th>Nombre</th><th>Edad</th><th>Riesgo</th></tr></thead>
                    <tbody>${d.censo.slice(0, 5).map(p => `<tr><td>${p.nombre}</td><td>${p.edad}</td><td>${p.nivel_riesgo}</td></tr>`).join('')}</tbody>
                </table>
            </div>
        ` : ''}
    `;
}

function renderPreviewMedico(d) {
    const res = d.resumen || {};
    return `
        <div class="preview-section">
            <h4 style="color: var(--gray-500); margin-bottom: 1rem; border-bottom: 2px solid var(--purple-light);">RESUMEN CLÍNICO</h4>
            <div class="preview-grid">
                <div class="preview-item"><span>Consultas:</span><span class="preview-value">${res.consultas_realizadas || 0}</span></div>
                <div class="preview-item"><span>Atendidas:</span><span class="preview-value">${res.pacientes_atendidas || 0}</span></div>
                <div class="preview-item"><span>Signos de Alarma:</span><span class="preview-value" style="color: var(--red);">${res.pacientes_con_signos_alarma || 0}</span></div>
            </div>
        </div>
        <div class="preview-section">
            <h4 style="color: var(--gray-500); margin-bottom: 0.5rem;">OBSERVACIONES</h4>
            <p style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid var(--gray-200); font-size: 0.875rem;">
                ${d.observaciones_generales || 'Sin observaciones adicionales.'}
            </p>
        </div>
    `;
}

function renderPreviewTS(d) {
    const res = d.resumen || {};
    return `
        <div class="preview-section">
            <h4 style="color: var(--gray-500); margin-bottom: 1rem; border-bottom: 2px solid var(--purple-light);">SEGUIMIENTO DE INASISTENCIAS</h4>
            <div class="preview-grid">
                <div class="preview-item"><span>Total Inasistencias:</span><span class="preview-value">${res.total_inasistencias || 0}</span></div>
                <div class="preview-item"><span>Justificadas:</span><span class="preview-value">${res.justificadas || 0}</span></div>
                <div class="preview-item"><span>Sin Justificación:</span><span class="preview-value">${res.sin_justificacion || 0}</span></div>
                <div class="preview-item"><span>Reintegradas:</span><span class="preview-value">${res.pacientes_reintegradas || 0}</span></div>
            </div>
        </div>
    `;
}

function renderPreviewDirector(d) {
    const kpis = d.kpis || {};
    return `
        <div class="preview-section">
            <h4 style="color: var(--gray-500); margin-bottom: 1rem; border-bottom: 2px solid var(--purple-light);">INDICADORES CLAVE (KPIs)</h4>
            <div class="preview-grid">
                <div class="preview-item"><span>Pacientes Activas:</span><span class="preview-value">${kpis.total_pacientes_activas || 0}</span></div>
                <div class="preview-item"><span>Consultas Mes:</span><span class="preview-value">${kpis.consultas_mes || 0}</span></div>
                <div class="preview-item"><span>Asistencia:</span><span class="preview-value">${kpis.tasa_asistencia || 0}%</span></div>
                <div class="preview-item"><span>Alto Riesgo:</span><span class="preview-value">${kpis.pacientes_alto_riesgo || 0}</span></div>
            </div>
        </div>
    `;
}

function closePreviewModal() {
    document.getElementById('modalPreview').style.display = 'none';
}

function descargarReporteId(id) {
    window.location.href = `/gestion/api/reportes/${id}/descargar`;
}
