document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.getElementById('query-input');
    const queryButton = document.getElementById('query-button');
    const resultsSection = document.getElementById('results-section');
    const loader = document.getElementById('loader');
    const responseContainer = document.getElementById('response-container');
    const llmResponse = document.getElementById('llm-response');
    const sourcesContainer = document.getElementById('sources-container');
    const errorMessage = document.getElementById('error-message');

    const handleQuery = async () => {
        const query = queryInput.value.trim();
        if (!query) {
            showError('Por favor, introduce una pregunta.');
            return;
        }

        // Reset UI
        resultsSection.classList.remove('hidden');
        responseContainer.classList.add('hidden');
        errorMessage.classList.add('hidden');
        loader.classList.remove('hidden');

        try {
            const response = await fetch('/consultar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ pregunta: query })
            });

            loader.classList.add('hidden');

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Ocurrió un error en el servidor.');
            }

            const data = await response.json();
            displayResults(data);

        } catch (error) {
            loader.classList.add('hidden');
            showError(error.message);
        }
    };

    const displayResults = (data) => {
        llmResponse.textContent = data.respuesta;
        sourcesContainer.innerHTML = '';

        if (data.noticias_relevantes && data.noticias_relevantes.length > 0) {
            data.noticias_relevantes.forEach(news => {
                const card = document.createElement('div');
                card.className = 'source-card';

                const title = document.createElement('h5');
                title.textContent = news.titulo;

                const content = document.createElement('p');
                content.textContent = news.contenido;

                const meta = document.createElement('div');
                meta.className = 'meta';
                
                const date = new Date(news.fecha);
                const formattedDate = date.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' });
                
                meta.innerHTML = `<span>${formattedDate} | ${news.media_id}</span><a href="${news.url}" target="_blank">Leer más</a>`;

                card.appendChild(title);
                card.appendChild(content);
                card.appendChild(meta);
                sourcesContainer.appendChild(card);
            });
        } else {
            sourcesContainer.innerHTML = '<p>No se utilizaron fuentes específicas para esta respuesta.</p>';
        }
        
        responseContainer.classList.remove('hidden');
    };

    const showError = (message) => {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    };

    queryButton.addEventListener('click', handleQuery);
    queryInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            handleQuery();
        }
    });
}); 