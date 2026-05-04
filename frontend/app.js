document.addEventListener('DOMContentLoaded', () => {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    let currentInputMode = 'texto';

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const target = btn.getAttribute('data-target');
            document.getElementById(target).classList.add('active');
            currentInputMode = target === 'tab-texto' ? 'texto' : 'foto';
        });
    });

    const uploadArea = document.querySelector('.upload-area');
    const fotoInput = document.getElementById('foto-input');
    const fileNameDisplay = document.getElementById('file-name');

    uploadArea.addEventListener('click', () => fotoInput.click());
    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault(); uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length) { fotoInput.files = e.dataTransfer.files; updateFileName(); }
    });
    fotoInput.addEventListener('change', updateFileName);

    function updateFileName() {
        if (fotoInput.files.length > 0) {
            fileNameDisplay.textContent = fotoInput.files[0].name;
            fileNameDisplay.style.color = '#4ade80';
            document.querySelector('.upload-area i').className = 'fa-solid fa-circle-check';
            document.querySelector('.upload-area i').style.color = '#4ade80';
        }
    }

    let userLat = null, userLon = null;
    const btnLocation = document.getElementById('btn-location');
    const locationStatus = document.getElementById('location-status');

    btnLocation.addEventListener('click', () => {
        locationStatus.textContent = '📍 Buscando...';
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    userLat = pos.coords.latitude; userLon = pos.coords.longitude;
                    locationStatus.textContent = '📍 Ubicación capturada con éxito';
                    locationStatus.style.color = '#4ade80'; btnLocation.style.display = 'none';
                },
                (err) => {
                    locationStatus.textContent = '❌ Ubicación bloqueada. Usando CDMX (Zócalo).';
                    userLat = 19.4326; userLon = -99.1332;
                }
            );
        }
    });

    const btnCalcular = document.getElementById('btn-calcular');
    const loadingOverlay = document.getElementById('loading-overlay');
    const resultsSection = document.getElementById('results-section');
    const resultsContainer = document.getElementById('results-container');

    btnCalcular.addEventListener('click', async () => {
        if (!userLat || !userLon) {
            alert('Por favor, haz clic en "Obtener mi ubicación" primero.');
            return;
        }

        let endpoint = '', options = {};

        if (currentInputMode === 'texto') {
            const texto = document.getElementById('lista-texto').value;
            if (!texto) { alert('Escribe algunos productos.'); return; }
            const productos = texto.split(',').map(p => p.trim()).filter(p => p);
            endpoint = '/api/v1/optimizar-carrito';
            options = { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ubicacion_usuario: { latitud: userLat, longitud: userLon }, productos }) };
        } else {
            if (!fotoInput.files.length) { alert('Selecciona una foto primero.'); return; }
            const formData = new FormData();
            formData.append('foto', fotoInput.files[0]);
            formData.append('latitud', userLat); formData.append('longitud', userLon);
            endpoint = '/api/v1/analizar-foto';
            options = { method: 'POST', body: formData };
        }

        loadingOverlay.classList.remove('hidden'); resultsSection.classList.add('hidden');
        try {
            const res = await fetch(endpoint, options);
            if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Error en servidor'); }
            const data = await res.json();
            renderResults(data.resultados);
            resultsSection.classList.remove('hidden'); resultsSection.scrollIntoView({ behavior: 'smooth' });
        } catch (err) { alert('Aviso: ' + err.message + '\n\n(Asegúrate de que Docker esté corriendo y Gemini tenga API Key)'); } finally { loadingOverlay.classList.add('hidden'); }
    });

    function renderResults(resultados) {
        resultsContainer.innerHTML = '';
        if (!resultados || resultados.length === 0) {
            resultsContainer.innerHTML = '<p style="text-align:center">No se encontraron tiendas cercanas.</p>'; return;
        }
        resultados.forEach(res => {
            const card = document.createElement('div'); card.className = 'card';
            let icon = 'fa-building';
            if(res.cadena.toLowerCase().includes('walmart')) icon = 'fa-cart-shopping';
            else if(res.cadena.toLowerCase().includes('soriana')) icon = 'fa-basket-shopping';
            let missingItemsHtml = '';
            if (res.productos_no_encontrados && res.productos_no_encontrados.length > 0) {
                missingItemsHtml = `
                    <div style="margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid #334155; font-size: 0.85rem; color: #94a3b8;">
                        <i class="fa-solid fa-triangle-exclamation" style="color: #fbbf24;"></i>
                        Artículos no encontrados: <span style="color: #e2e8f0;">${res.productos_no_encontrados.join(', ')}</span>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="store-info">
                    <h3><i class="fa-solid ${icon}"></i> ${res.cadena}</h3>
                    <div class="store-details">
                        <span><i class="fa-solid fa-map-location-dot"></i> ${res.sucursal}</span>
                        <span><i class="fa-solid fa-road"></i> ${res.distancia_km} km</span>
                    </div>
                    <div class="store-details" style="margin-top:0.5rem; color:#4ade80;">
                        <i class="fa-solid fa-check"></i> ${res.productos_encontrados.length} prod.
                    </div>
                </div>
                <div class="price-info">
                    <div class="total-price">$${res.total_viaje.toFixed(2)}</div>
                    <div class="sub-price">Carro: $${res.subtotal_productos.toFixed(2)}</div>
                    <div class="sub-price"><i class="fa-solid fa-gas-pump"></i> Gas: $${res.costo_gasolina.toFixed(2)}</div>
                </div>
                ${missingItemsHtml}
            `;
            resultsContainer.appendChild(card);
        });
    }
});
