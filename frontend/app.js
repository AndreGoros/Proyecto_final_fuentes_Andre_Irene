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
    const listaTexto = document.getElementById('lista-texto');

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
            const texto = listaTexto.value;
            if (!texto) { alert('Escribe algunos productos.'); return; }
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
        } catch (err) { 
            alert('Aviso: ' + err.message); 
        } finally { 
            loadingOverlay.classList.add('hidden'); 
        }
    });

    const modalOverlay = document.getElementById('modal-overlay');
    const modalBody = document.getElementById('modal-body');
    const btnCloseModal = document.getElementById('close-modal');

    btnCloseModal.addEventListener('click', () => modalOverlay.classList.add('hidden'));
    modalOverlay.addEventListener('click', (e) => { if(e.target === modalOverlay) modalOverlay.classList.add('hidden'); });

    function renderResults(data) {
        resultsContainer.innerHTML = '';
        const { mejores_completos, mejores_incompletos } = data;

        if (!mejores_completos?.length && !mejores_incompletos?.length) {
            resultsContainer.innerHTML = '<p style="text-align:center">No se encontraron tiendas cercanas.</p>';
            return;
        }

        const allResults = [
            ...(mejores_completos || []).map(r => ({...r, type: 'completo'})),
            ...(mejores_incompletos || []).map(r => ({...r, type: 'incompleto'}))
        ];

        allResults.forEach((res, index) => {
            const card = createMiniCard(res, index === 0 && res.type === 'completo');
            card.addEventListener('click', () => openModal(res));
            resultsContainer.appendChild(card);
        });
    }

    function createMiniCard(res, isRecommended) {
        const card = document.createElement('div');
        card.className = `card-mini ${isRecommended ? 'recommended' : ''} ${res.type === 'incompleto' ? 'incompleto' : ''}`;
        
        card.innerHTML = `
            <div>
                <div style="font-size: 0.7rem; color: var(--primary); font-weight: 800; margin-bottom: 0.2rem;">
                    ${res.type === 'completo' ? 'LISTA COMPLETA' : 'INCOMPLETO'}
                </div>
                <h3>${res.cadena}</h3>
                <div class="dist">${res.sucursal.substring(0, 25)}...</div>
            </div>
            <div>
                <div class="price">$${res.total_viaje.toFixed(0)}</div>
                <div class="dist">${res.distancia_km.toFixed(1)} km</div>
            </div>
        `;
        return card;
    }

    function openModal(res) {
        const listaProdHTML = res.productos_encontrados.map(p => `
            <div class="product-item">
                <span><small>${p.cantidad}x</small> ${p.producto}</span>
                <b style="color:#4ade80">$${p.precio_total.toFixed(2)}</b>
            </div>
            <div style="font-size:0.7rem; color:var(--text-muted); margin-bottom:0.6rem; text-align:right">u: $${p.precio_unitario.toFixed(2)}</div>
        `).join('');

        const faltantesHTML = res.type === 'incompleto' ? `
            <div class="missing-items" style="margin-top:1rem; padding:1rem; background:rgba(248,113,113,0.1); border-radius:10px;">
                <h4 style="color:#f87171"><i class="fa-solid fa-circle-xmark"></i> Faltantes:</h4>
                <div class="missing-list" style="color:#fca5a5">${res.productos_no_encontrados.join(', ')}</div>
            </div>
        ` : '';

        modalBody.innerHTML = `
            <div style="text-align:center; margin-bottom:2rem;">
                <h2 style="font-size:2rem; margin-bottom:0.5rem;">${res.cadena}</h2>
                <p style="color:var(--text-muted)"><i class="fa-solid fa-location-dot"></i> ${res.sucursal}</p>
                <p style="font-size:0.8rem; opacity:0.7;">${res.direccion}</p>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:2rem;">
                <div>
                    <h4 style="margin-bottom:1rem;"><i class="fa-solid fa-check-double"></i> Detalle de Compra</h4>
                    ${listaProdHTML}
                    ${faltantesHTML}
                </div>
                <div style="display:flex; flex-direction:column; gap:1rem;">
                    <div class="glass-panel" style="padding:1.5rem; text-align:center;">
                        <div style="font-size:0.9rem; color:var(--text-muted);">Total Estimado</div>
                        <div style="font-size:3rem; font-weight:800; color:#4ade80;">$${res.total_viaje.toFixed(2)}</div>
                    </div>
                    <div style="padding:1rem; background:rgba(255,255,255,0.05); border-radius:10px; font-size:0.9rem;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                            <span>🛒 Subtotal:</span> <b>$${res.subtotal_productos.toFixed(2)}</b>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <span>⛽ Gasolina:</span> <b>$${res.costo_gasolina.toFixed(2)}</b>
                        </div>
                        <div style="display:flex; justify-content:space-between; border-top:1px solid rgba(255,255,255,0.1); padding-top:0.5rem; margin-top:0.5rem;">
                            <span>📍 Distancia:</span> <b>${res.distancia_km.toFixed(1)} km</b>
                        </div>
                    </div>
                </div>
            </div>
        `;

        modalOverlay.classList.remove('hidden');
    }
});
