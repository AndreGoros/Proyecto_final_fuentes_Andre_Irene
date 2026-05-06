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
            // Permitir que la lista venga separada por comas O por saltos de línea
            const productos = texto.split(/,|\n/).map(p => p.trim()).filter(p => p);
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
            renderResults(data);
            resultsSection.classList.remove('hidden'); resultsSection.scrollIntoView({ behavior: 'smooth' });
        } catch (err) { alert('Aviso: ' + err.message + '\n\n(Asegúrate de que Docker esté corriendo y Gemini tenga API Key)'); } finally { loadingOverlay.classList.add('hidden'); }
    });

    function renderResults(data) {
        resultsContainer.innerHTML = '';
        const { mejores_completos, mejores_incompletos } = data;

        if (!mejores_completos?.length && !mejores_incompletos?.length) {
            resultsContainer.innerHTML = '<p style="text-align:center">No se encontraron tiendas cercanas.</p>';
            return;
        }

        if (mejores_completos && mejores_completos.length > 0) {
            const header = document.createElement('div');
            header.className = 'section-header header-completos';
            header.innerHTML = '<h3><i class="fa-solid fa-circle-check"></i> Tiendas con Lista Completa</h3><p style="font-size:0.8rem; opacity:0.8">Estas opciones aseguran cubrir todos tus productos al mejor precio.</p>';
            resultsContainer.appendChild(header);
            mejores_completos.forEach(res => resultsContainer.appendChild(createCard(res, false)));
        }

        if (mejores_incompletos && mejores_incompletos.length > 0) {
            const header = document.createElement('div');
            header.className = 'section-header header-incompletos';
            header.innerHTML = '<h3><i class="fa-solid fa-triangle-exclamation"></i> Otras Opciones (Incompletas)</h3>';
            resultsContainer.appendChild(header);

            const warning = document.createElement('div');
            warning.className = 'warning-box';
            warning.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> AVISO: Las siguientes opciones no aseguran cubrir la lista completa.';
            resultsContainer.appendChild(warning);
            mejores_incompletos.forEach(res => resultsContainer.appendChild(createCard(res, true)));
        }
    }

    function createCard(res, isIncompleto) {
        const card = document.createElement('div');
        card.className = 'card';

        const listaProdHTML = res.productos_encontrados.map(p => `
            <div class="product-item">
                <span><small>${p.cantidad}x</small> ${p.producto}</span>
                <span style="font-weight:600">$${p.precio_total.toFixed(2)}</span>
            </div>
            <div style="font-size:0.7rem; color:var(--text-muted); margin-bottom:0.6rem; text-align:right">u: $${p.precio_unitario.toFixed(2)}</div>
        `).join('');

        const faltantesHTML = isIncompleto ? `
            <div class="missing-items">
                <h4><i class="fa-solid fa-circle-xmark"></i> Faltantes:</h4>
                <div class="missing-list">${res.productos_no_encontrados.join(', ')}</div>
            </div>
        ` : '';

        card.innerHTML = `
            <div class="card-top">
                <div class="store-info">
                    <h3><i class="fa-solid fa-shop"></i> ${res.cadena}</h3>
                    <div class="store-details">
                        <div style="margin-bottom: 0.3rem;"><i class="fa-solid fa-location-dot"></i> ${res.sucursal}</div>
                        <div style="font-size: 0.75rem; opacity: 0.8; margin-bottom: 0.5rem; line-height: 1.2;"><i class="fa-solid fa-map-pin"></i> ${res.direccion}</div>
                        <span><i class="fa-solid fa-road"></i> ${res.distancia_km.toFixed(1)} km</span>
                    </div>
                </div>
                <div class="price-info">
                    <div class="total-price">$${res.total_viaje.toFixed(2)}</div>
                    <div class="sub-price">Total estimado (incl. viaje)</div>
                </div>
            </div>

            <div class="card-content">
                <div class="products-found">
                    <h4><i class="fa-solid fa-check-double"></i> Productos Encontrados:</h4>
                    ${listaProdHTML}
                </div>
                
                <div class="summary-side">
                    <div class="cost-breakdown" style="font-size: 0.85rem; padding:1rem; background:rgba(255,255,255,0.05); border-radius:10px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:0.5rem">
                            <span>🛒 Carro:</span> <b>$${res.subtotal_productos.toFixed(2)}</b>
                        </div>
                        <div style="display:flex; justify-content:space-between">
                            <span>⛽ Gasolina:</span> <b>$${res.costo_gasolina.toFixed(2)}</b>
                        </div>
                    </div>
                    
                    ${faltantesHTML}
                </div>
            </div>
        `;
        return card;
    }
});
