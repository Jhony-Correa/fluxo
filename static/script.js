function iniGraf(ent, desp) {
    const ctx = document.getElementById('grafFin').getContext('2d');
    if (window.mGraf) window.mGraf.destroy();
    window.mGraf = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Entradas', 'Despesas'],
            datasets: [{
                data: [ent, desp],
                backgroundColor: ['#27ae60', '#c0392b'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 20, font: { size: 14 } }
                }
            }
        }
    });
}

function abrirMod() {
    document.getElementById('modFin').style.display = 'block';
}

function fecharMod() {
    document.getElementById('modFin').style.display = 'none';
}

document.addEventListener("DOMContentLoaded", function() {
    const avisos = document.querySelectorAll('.alerta');
    avisos.forEach(function(a) {
        setTimeout(function() {
            a.classList.add('ocultar');
            setTimeout(function() { a.remove(); }, 500);
        }, 5000);
    });
});