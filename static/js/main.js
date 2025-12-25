document.addEventListener('DOMContentLoaded', function () {
	const toggle = document.getElementById('sidebarToggle');
	const sidebar = document.querySelector('.sidebar');
	if (toggle && sidebar) {
		toggle.addEventListener('click', () => {
			sidebar.classList.toggle('show');
		});
	}

	// Fecha actual
	const dateEl = document.getElementById('current-date');
	if (dateEl) {
		const now = new Date();
		const opts = { year: 'numeric', month: 'short', day: 'numeric' };
		dateEl.textContent = now.toLocaleDateString('es-ES', opts);
	}

	// Cerrar sidebar en click fuera (móvil)
	document.addEventListener('click', (e) => {
		if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
			sidebar.classList.remove('show');
		}
	});
});
