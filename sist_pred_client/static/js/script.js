// main.js - Sistema ChurnPredict
class ChurnPredictSystem {
    constructor() {
        this.init();
    }

    init() {
        console.log('Sistema ChurnPredict inicializado');
        
        this.initSidebar();
        this.initDateTime();
        this.initNotifications();
        this.initSearch();
        this.initDeleteConfirmations();
        this.initSystemStats();
        this.initTooltips();
        this.initLoadingOverlay();
        this.initPageAnimations();
    }

    // 1. Sidebar Toggle
    initSidebar() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');
        
        if (!sidebarToggle || !sidebar) return;
        
        sidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('active');
            
            if (window.innerWidth > 992) {
                if (sidebar.classList.contains('active')) {
                    sidebar.style.width = '70px';
                    mainContent.style.marginLeft = '70px';
                    mainContent.style.width = 'calc(100% - 70px)';
                } else {
                    sidebar.style.width = '260px';
                    mainContent.style.marginLeft = '260px';
                    mainContent.style.width = 'calc(100% - 260px)';
                }
            }
        });

        // Cerrar sidebar al hacer clic fuera (en móviles)
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 992) {
                if (!sidebar.contains(e.target) && 
                    !sidebarToggle.contains(e.target) && 
                    sidebar.classList.contains('active')) {
                    sidebar.classList.remove('active');
                }
            }
        });

        // Cerrar sidebar con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });
    }

    // 2. Fecha y Hora Actual
    initDateTime() {
        const updateDateTime = () => {
            const now = new Date();
            const options = { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            
            const dateElement = document.getElementById('current-date');
            if (dateElement) {
                dateElement.textContent = now.toLocaleDateString('es-ES', options);
            }
        };
        
        updateDateTime();
        setInterval(updateDateTime, 60000); // Actualizar cada minuto
    }

    // 3. Notificaciones
    initNotifications() {
        // Simular actualización de notificaciones
        setTimeout(() => {
            const alertBadge = document.getElementById('clientes-alerta');
            if (alertBadge) {
                // Simular 3 clientes en alto riesgo
                alertBadge.textContent = '3';
                this.animateBadge(alertBadge);
            }
        }, 2000);

        // Contador de notificaciones no leídas
        const notificationBadge = document.querySelector('.notification-badge');
        if (notificationBadge) {
            setInterval(() => {
                if (Math.random() > 0.8) {
                    const current = parseInt(notificationBadge.textContent) || 0;
                    notificationBadge.textContent = current + 1;
                    this.animateBadge(notificationBadge);
                }
            }, 30000);
        }
    }

    // 4. Búsqueda
    initSearch() {
        const searchInput = document.querySelector('.search-box input');
        const searchBtn = document.querySelector('.search-btn');
        
        if (!searchInput) return;
        
        // Buscar al presionar Enter
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch(searchInput.value);
            }
        });
        
        // Buscar al hacer clic en el botón
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.performSearch(searchInput.value);
            });
        }
        
        // Autocompletar
        searchInput.addEventListener('input', (e) => {
            if (e.target.value.length > 2) {
                this.showSearchSuggestions(e.target.value);
            }
        });
    }

    // 5. Confirmaciones de eliminación
    initDeleteConfirmations() {
        document.addEventListener('click', (e) => {
            const deleteBtn = e.target.closest('.btn-delete, .btn-eliminar, [data-action="delete"]');
            
            if (deleteBtn && deleteBtn.tagName === 'A') {
                e.preventDefault();
                this.confirmDelete(deleteBtn.href, deleteBtn);
            } else if (deleteBtn && deleteBtn.type === 'submit') {
                e.preventDefault();
                this.confirmDelete(null, deleteBtn);
            }
        });
    }

    // 6. Estadísticas del sistema
    initSystemStats() {
        const statsElement = document.getElementById('system-stats');
        if (!statsElement) return;
        
        const updateStats = () => {
            const stats = {
                clientes: Math.floor(Math.random() * 500) + 1000,
                predicciones: Math.floor(Math.random() * 300) + 500,
                accuracy: (Math.random() * 5 + 92.5).toFixed(1)
            };
            
            statsElement.innerHTML = 
                `${stats.clientes} clientes | ${stats.predicciones} análisis | ${stats.accuracy}% accuracy`;
        };
        
        updateStats();
        setInterval(updateStats, 60000); // Actualizar cada minuto
    }

    // 7. Tooltips
    initTooltips() {
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(
                document.querySelectorAll('[data-bs-toggle="tooltip"]')
            );
            
            tooltipTriggerList.map(tooltipTriggerEl => {
                return new bootstrap.Tooltip(tooltipTriggerEl, {
                    delay: { show: 500, hide: 100 }
                });
            });
        }
    }

    // 8. Loading Overlay
    initLoadingOverlay() {
        // Interceptar enlaces con data-loading
        document.querySelectorAll('a[data-loading]').forEach(link => {
            link.addEventListener('click', () => {
                this.showLoading();
            });
        });

        // Interceptar formularios
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', () => {
                this.showLoading();
            });
        });

        // Ocultar loading cuando se carga la página
        window.addEventListener('load', () => {
            setTimeout(() => this.hideLoading(), 500);
        });
    }

    // 9. Animaciones de página
    initPageAnimations() {
        // Animar elementos al cargar
        setTimeout(() => {
            document.querySelectorAll('.card, .stat-card, .table-container').forEach((el, i) => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0)';
                }, i * 100);
            });
        }, 300);
    }

    // ===== MÉTODOS AUXILIARES =====
    
    performSearch(query) {
        if (!query.trim()) return;
        
        this.showLoading();
        
        // Simular búsqueda
        setTimeout(() => {
            this.hideLoading();
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: 'Resultados de búsqueda',
                    text: `Buscando: "${query}"`,
                    icon: 'info',
                    confirmButtonText: 'OK'
                });
            } else {
                alert(`Buscando: "${query}"`);
            }
        }, 1000);
    }

    showSearchSuggestions(query) {
        // En una implementación real, aquí harías una petición AJAX
        console.log('Mostrar sugerencias para:', query);
    }

    confirmDelete(url, element) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '¿Estás seguro?',
                text: "Esta acción no se puede deshacer",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#f72585',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar',
                reverseButtons: true,
                backdrop: true,
                allowOutsideClick: false
            }).then((result) => {
                if (result.isConfirmed) {
                    this.showLoading();
                    
                    setTimeout(() => {
                        this.hideLoading();
                        
                        if (url) {
                            window.location.href = url;
                        } else if (element && element.closest('form')) {
                            element.closest('form').submit();
                        }
                        
                        Swal.fire(
                            '¡Eliminado!',
                            'El registro ha sido eliminado.',
                            'success'
                        );
                    }, 1500);
                }
            });
        } else if (confirm('¿Estás seguro de eliminar este elemento?')) {
            if (url) {
                window.location.href = url;
            } else if (element && element.closest('form')) {
                element.closest('form').submit();
            }
        }
    }

    animateBadge(badge) {
        badge.style.transform = 'scale(1.3)';
        badge.style.transition = 'transform 0.3s ease';
        
        setTimeout(() => {
            badge.style.transform = 'scale(1)';
        }, 300);
    }

    showLoading(message = 'Procesando solicitud...') {
        const modal = document.getElementById('loadingModal');
        if (!modal) return;
        
        const modalBody = modal.querySelector('.modal-body p');
        if (modalBody) {
            modalBody.textContent = message;
        }
        
        if (typeof bootstrap !== 'undefined') {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        } else {
            modal.style.display = 'block';
        }
    }

    hideLoading() {
        const modal = document.getElementById('loadingModal');
        if (!modal) return;
        
        if (typeof bootstrap !== 'undefined') {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        } else {
            modal.style.display = 'none';
        }
    }

    // Método para filtrar tablas
    filterTable(tableId, searchTerm) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm.toLowerCase()) ? '' : 'none';
        });
    }

    // Método para ordenar tablas
    sortTable(tableId, column, direction = 'asc') {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aVal = a.children[column]?.textContent || '';
            const bVal = b.children[column]?.textContent || '';
            
            if (!isNaN(aVal) && !isNaN(bVal)) {
                return direction === 'asc' ? aVal - bVal : bVal - aVal;
            }
            
            return direction === 'asc' 
                ? aVal.localeCompare(bVal) 
                : bVal.localeCompare(aVal);
        });
        
        // Reordenar filas
        rows.forEach(row => tbody.appendChild(row));
    }
}

// ===== FUNCIONES GLOBALES =====

// Mostrar notificación de éxito
window.showSuccess = function(message, title = '¡Éxito!') {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: title,
            text: message,
            icon: 'success',
            timer: 3000,
            showConfirmButton: false,
            toast: true,
            position: 'top-end'
        });
    } else {
        alert(message);
    }
};

// Mostrar error
window.showError = function(message, title = 'Error') {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: title,
            text: message,
            icon: 'error',
            confirmButtonColor: '#f72585'
        });
    } else {
        alert('ERROR: ' + message);
    }
};

// Mostrar advertencia
window.showWarning = function(message, title = 'Advertencia') {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: title,
            text: message,
            icon: 'warning',
            confirmButtonColor: '#ff9e00'
        });
    } else {
        alert('ADVERTENCIA: ' + message);
    }
};

// Exportar datos
window.exportData = function(format = 'csv') {
    window.Sistema.showLoading(`Exportando datos en formato ${format.toUpperCase()}...`);
    
    setTimeout(() => {
        window.Sistema.hideLoading();
        window.showSuccess(`Datos exportados en formato ${format.toUpperCase()}`);
    }, 2000);
};

// ===== INICIALIZACIÓN =====

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.Sistema = new ChurnPredictSystem();
    
    // Detectar cambios en conexión
    window.addEventListener('online', () => {
        window.showSuccess('Conexión a internet restablecida');
    });
    
    window.addEventListener('offline', () => {
        window.showWarning('Se ha perdido la conexión a internet');
    });
    
    // Guardar estado del sidebar
    window.addEventListener('beforeunload', () => {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('active') ? 'true' : 'false');
        }
    });
    
    // Cargar estado del sidebar
    const sidebar = document.querySelector('.sidebar');
    if (sidebar && localStorage.getItem('sidebar-collapsed') === 'true') {
        sidebar.classList.add('active');
        const mainContent = document.querySelector('.main-content');
        if (mainContent && window.innerWidth > 992) {
            sidebar.style.width = '70px';
            mainContent.style.marginLeft = '70px';
            mainContent.style.width = 'calc(100% - 70px)';
        }
    }
    
    // Inicializar tooltips de Bootstrap
    if (typeof bootstrap !== 'undefined') {
        // Tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        
        // Popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }
    
    // Añadir clase active al menú según la URL actual
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// Hacer disponible para consola
console.info('ChurnPredict System cargado. Usa window.Sistema para acceder a las funciones.');