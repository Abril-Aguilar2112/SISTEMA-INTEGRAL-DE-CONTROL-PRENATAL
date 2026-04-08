document.addEventListener('DOMContentLoaded', function() {
    const editBtns = document.querySelectorAll('#edit-btn, .edit-btn-trigger');
    const saveBtn = document.getElementById('save-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const printBtn = document.getElementById('print-btn');
    const form = document.getElementById('censo-form');
    const inputs = form.querySelectorAll('input:not([type="hidden"]), select, textarea');
    const dataValues = document.querySelectorAll('.data-value:not(.no-edit)');
    const editActions = document.getElementById('edit-actions');
    const initialActions = document.getElementById('initial-actions');
    const msgContainer = document.getElementById('ui-message-container');
    const msgDiv = document.getElementById('ui-message');
    const msgText = document.getElementById('ui-message-text');

    function showUIMessage(message, type = 'success') {
        msgContainer.classList.remove('hidden');
        msgDiv.className = `alert alert-${type}`;
        msgText.textContent = message;
        
        if (type === 'success') {
            setTimeout(() => {
                msgContainer.classList.add('hidden');
            }, 5000);
        }
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function enterEditMode() {
        initialActions.classList.add('hidden');
        editActions.classList.remove('hidden');
        
        dataValues.forEach(val => val.classList.add('hidden'));
        inputs.forEach(input => {
            if (!input.hasAttribute('readonly')) {
                input.classList.remove('hidden');
            }
        });
        
        document.querySelectorAll('.data-field').forEach(field => {
            if (field.querySelector('input:not([readonly]), select, textarea')) {
                field.classList.add('editing');
            }
        });
    }

    function exitEditMode() {
        initialActions.classList.remove('hidden');
        editActions.classList.add('hidden');
        
        dataValues.forEach(val => val.classList.remove('hidden'));
        inputs.forEach(input => input.classList.add('hidden'));
        
        document.querySelectorAll('.data-field').forEach(field => {
            field.classList.remove('editing');
        });
    }

    if (editBtns.length > 0) {
        editBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                enterEditMode();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', function(e) {
            e.preventDefault();
            exitEditMode();
            form.reset();
        });
    }

    if (printBtn) {
        printBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    }

    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    showUIMessage('Registro actualizado correctamente', 'success');
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else {
                    showUIMessage('Error: ' + (result.message || 'Error desconocido'), 'danger');
                }
                
            } catch (error) {
                console.error('Error:', error);
                showUIMessage('Ocurrió un error al actualizar el registro', 'danger');
            }
        });
    }
});
