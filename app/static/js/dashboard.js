document.addEventListener('DOMContentLoaded', function () {
    fetch('/estadisticas')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            populateKPIs(data.estadisticas_generales);
            renderMediaChart(data.estadisticas_por_medio);
            renderClassificationChart(data.estadisticas_generales);
        })
        .catch(error => {
            console.error('Error fetching dashboard data:', error);
            // Optionally, display an error message to the user
            const container = document.querySelector('.container');
            container.innerHTML = '<h2>Error al cargar las estadísticas</h2><p>No se pudieron obtener los datos del servidor. Por favor, inténtelo de nuevo más tarde.</p>';
        });
});

function populateKPIs(stats) {
    document.getElementById('kpi-total-noticias').textContent = stats.total_noticias;
    document.getElementById('kpi-accidentes').textContent = stats.cantidad_accidentes;
    document.getElementById('kpi-no-accidentes').textContent = stats.cantidad_no_accidentes;
    document.getElementById('kpi-sin-clasificar').textContent = stats.cantidad_sin_clasificar;
}

function renderMediaChart(mediaStats) {
    const ctx = document.getElementById('media-chart').getContext('2d');
    
    const labels = Object.keys(mediaStats);
    const data = labels.map(label => mediaStats[label].total_noticias);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total de Noticias',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function renderClassificationChart(stats) {
    const ctx = document.getElementById('classification-chart').getContext('2d');
    
    const data = {
        labels: ['Accidentes', 'No Accidentes', 'Sin Clasificar'],
        datasets: [{
            data: [
                stats.cantidad_accidentes,
                stats.cantidad_no_accidentes,
                stats.cantidad_sin_clasificar
            ],
            backgroundColor: [
                'rgba(255, 99, 132, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(201, 203, 207, 0.7)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(201, 203, 207, 1)'
            ],
            borderWidth: 1
        }]
    };

    new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
} 