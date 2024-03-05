// static/scripts.js

// Función para cargar el total de servicios del día
function cargarTotalDia() {
    fetch('/sumar_servicios_dia')
        .then(response => response.json())
        .then(data => {
            document.getElementById('totalDia').textContent = data.total_dia.toFixed(2);
        })
        .catch(error => {
            console.error('Error al cargar el total del día:', error);
        });
}

// Función para cargar el total de servicios por mes
function cargarTotalMes() {
    fetch('/ver_servicios_mes')
        .then(response => response.json())
        .then(data => {
            document.getElementById('totalMes').textContent = data.total_mes.toFixed(2);
        })
        .catch(error => {
            console.error('Error al cargar el total del mes:', error);
        });
}

// Cargar totales cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    cargarTotalDia();
    cargarTotalMes();
});
