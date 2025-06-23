document.addEventListener('DOMContentLoaded', () => {
    const runScrapersBtn = document.getElementById('run-scrapers-btn');
    const scrapersLog = document.getElementById('scrapers-log');
    const fechaLimiteInput = document.getElementById('fecha-limite-scrapers');
    const runClassifiersBtn = document.getElementById('run-classifiers-btn');
    const classifiersLog = document.getElementById('classifiers-log');

    const handleRunTask = async (button, logElement, url) => {
        // Deshabilitar ambos botones para evitar ejecuciones concurrentes
        runScrapersBtn.disabled = true;
        runClassifiersBtn.disabled = true;
        button.textContent = 'Ejecutando...';

        // Preparar el área de logs
        logElement.style.display = 'block';
        logElement.textContent = 'Iniciando tarea...\n';
        
        try {
            const response = await fetch(url, { method: 'POST' });
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    logElement.textContent += '\n✅ Tarea completada.\n';
                    break;
                }
                const chunk = decoder.decode(value, { stream: true });
                logElement.textContent += chunk;
                // Auto-scroll hacia el final
                logElement.scrollTop = logElement.scrollHeight;
            }

        } catch (error) {
            logElement.textContent += `\n❌ Error al ejecutar la tarea: ${error.message}\n`;
        } finally {
            // Rehabilitar ambos botones
            runScrapersBtn.disabled = false;
            runClassifiersBtn.disabled = false;
            button.textContent = 'Ejecutar Todos';
        }
    };

    runScrapersBtn.addEventListener('click', () => {
        let url = '/acciones/ejecutar-scrapers';
        const fechaLimite = fechaLimiteInput.value;
        if (fechaLimite) {
            url += `?fecha_limite=${fechaLimite}`;
        }
        handleRunTask(runScrapersBtn, scrapersLog, url);
    });

    runClassifiersBtn.addEventListener('click', () => {
        handleRunTask(runClassifiersBtn, classifiersLog, '/acciones/ejecutar-clasificadores');
    });
}); 