function openReagendarModal(idCita, fecha, hora) {
  const dlg = document.getElementById("modalReagendar");
  const form = document.getElementById("formReagendar");
  const base = document.body.dataset.reagendarBase || "";
  form.action = base.replace(/0$/, String(idCita));

  document.getElementById("reagendarFecha").value = fecha || "";

  const horaStr = (hora || "").toString();
  const timeValue = horaStr.includes(":") ? horaStr.slice(0, 5) : "";
  document.getElementById("reagendarHora").value = timeValue;

  dlg.classList.remove("closing");
  dlg.showModal();
}

function openJustificarModal(idCita) {
  const dlg = document.getElementById("modalJustificar");
  const form = document.getElementById("formJustificar");
  const base = document.body.dataset.justificarBase || "";
  form.action = base.replace(/0$/, String(idCita));

  document.getElementById("justificarMotivo").value = "";

  dlg.classList.remove("closing");
  dlg.showModal();
}

function closeModal(id) {
  const dlg = document.getElementById(id);
  if (!dlg || !dlg.open) return;

  dlg.classList.add("closing");
  window.setTimeout(() => {
    try {
      dlg.close();
    } finally {
      dlg.classList.remove("closing");
    }
  }, 160);
}

function wireModalBehavior(dlg) {
  if (!dlg) return;

  dlg.addEventListener("cancel", (e) => {
    e.preventDefault();
    closeModal(dlg.id);
  });

  dlg.addEventListener("click", (e) => {
    const rect = dlg.getBoundingClientRect();
    const inDialog =
      rect.top <= e.clientY &&
      e.clientY <= rect.top + rect.height &&
      rect.left <= e.clientX &&
      e.clientX <= rect.left + rect.width;

    if (!inDialog) {
      closeModal(dlg.id);
    }
  });
}

window.addEventListener("DOMContentLoaded", () => {
  wireModalBehavior(document.getElementById("modalReagendar"));
  wireModalBehavior(document.getElementById("modalJustificar"));
});
