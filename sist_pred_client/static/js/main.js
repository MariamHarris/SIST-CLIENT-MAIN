document.addEventListener('DOMContentLoaded', function () {
  // Fecha en topbar
  const dateEl = document.getElementById('current-date');
  if (dateEl) {
    try {
      const now = new Date();
      dateEl.textContent = now.toLocaleDateString('es-ES', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      // noop
    }
  }

  // Estado del sistema (placeholder liviano)
  const statsEl = document.getElementById('system-stats');
  if (statsEl) {
    statsEl.textContent = 'OK';
  }

  // Si el sidebar está abierto en móvil, cerrarlo al navegar
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) {
    document.querySelectorAll('.sidebar a').forEach((a) => {
      a.addEventListener('click', () => {
        if (window.innerWidth <= 768 && sidebar.classList.contains('active')) {
          sidebar.classList.remove('active');
        }
      });
    });
  }
});
