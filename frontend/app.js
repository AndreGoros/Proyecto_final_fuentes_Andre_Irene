// ── Logos de cadenas (usando Google Favicon CDN + fallback emoji) ────────────
const CHAIN_CONFIG = {
    'walmart':          { logo: 'https://logo.clearbit.com/walmart.com.mx',    color: '#0071ce', emoji: '🛒' },
    'chedraui':         { logo: 'https://logo.clearbit.com/chedraui.com.mx',   color: '#e31837', emoji: '🛒' },
    'soriana':          { logo: 'https://logo.clearbit.com/soriana.com',        color: '#009444', emoji: '🛒' },
    'costco':           { logo: 'https://logo.clearbit.com/costco.com.mx',      color: '#005daa', emoji: '🏪' },
    'bodega aurrera':   { logo: 'https://logo.clearbit.com/bodegaaurrera.com.mx', color: '#f5a623', emoji: '🛒' },
    'aurrera':          { logo: 'https://logo.clearbit.com/bodegaaurrera.com.mx', color: '#f5a623', emoji: '🛒' },
    'sam\'s club':      { logo: 'https://logo.clearbit.com/samsclub.com.mx',    color: '#0071ce', emoji: '🏪' },
    'superama':         { logo: 'https://logo.clearbit.com/walmart.com.mx',    color: '#6dae43', emoji: '🥦' },
    'la comer':         { logo: 'https://logo.clearbit.com/lacomer.com.mx',    color: '#e6001e', emoji: '🛒' },
    'city market':      { logo: 'https://logo.clearbit.com/citymarket.com.mx', color: '#a0262a', emoji: '🛒' },
    'fresko':           { logo: 'https://logo.clearbit.com/lacomer.com.mx',    color: '#78b83a', emoji: '🥬' },
    'mega':             { logo: 'https://logo.clearbit.com/soriana.com',        color: '#e31837', emoji: '🛒' },
};

function getChainConfig(cadena) {
    const key = (cadena || '').toLowerCase().trim();
    for (const [name, cfg] of Object.entries(CHAIN_CONFIG)) {
        if (key.includes(name)) return cfg;
    }
    return { logo: null, color: '#00d2ff', emoji: '🏪' };
}

function getChainLogoHTML(cadena, size = 40) {
    const cfg = getChainConfig(cadena);
    if (cfg.logo) {
        return `<img 
            src="${cfg.logo}" 
            alt="${cadena}" 
            class="chain-logo" 
            style="width:${size}px;height:${size}px;border-radius:8px;object-fit:contain;background:white;padding:3px;"
            onerror="this.outerHTML='<span class=\\'chain-emoji\\'>${cfg.emoji}</span>'"
        >`;
    }
    return `<span class="chain-emoji" style="font-size:${size * 0.7}px">${cfg.emoji}</span>`;
}

// ── Inicialización ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

    // Tabs
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

    // Foto upload
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

    // Geolocalización
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
                () => {
                    locationStatus.textContent = '❌ Ubicación bloqueada. Usando CDMX (Zócalo).';
                    userLat = 19.4326; userLon = -99.1332;
                }
            );
        }
    });

    // Calcular
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

        loadingOverlay.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            const res = await fetch(endpoint, options);
            if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Error en servidor'); }
            const data = await res.json();
            renderResults(data);
            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        } catch (err) {
            alert('Aviso: ' + err.message);
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    });

    // Modal
    const modalOverlay = document.getElementById('modal-overlay');
    const modalBody = document.getElementById('modal-body');
    const btnCloseModal = document.getElementById('close-modal');

    btnCloseModal.addEventListener('click', () => modalOverlay.classList.add('hidden'));
    modalOverlay.addEventListener('click', (e) => { if (e.target === modalOverlay) modalOverlay.classList.add('hidden'); });

    // ── Render resultados ────────────────────────────────────────────────────
    function renderResults(data) {
        resultsContainer.innerHTML = '';
        const { mejores_completos, mejores_incompletos } = data;

        if (!mejores_completos?.length && !mejores_incompletos?.length) {
            resultsContainer.innerHTML = '<p style="text-align:center;color:var(--text-muted)">No se encontraron tiendas cercanas con estos productos.</p>';
            return;
        }

        // Calcular el precio máximo para la barra de progreso comparativa
        const allResults = [
            ...(mejores_completos || []).map(r => ({ ...r, type: 'completo' })),
            ...(mejores_incompletos || []).map(r => ({ ...r, type: 'incompleto' }))
        ];
        const maxPrice = Math.max(...allResults.map(r => r.total_viaje));

        allResults.forEach((res, index) => {
            const card = createMiniCard(res, index === 0 && res.type === 'completo', maxPrice);
            card.addEventListener('click', () => openModal(res));
            resultsContainer.appendChild(card);

            // Animación escalonada
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 80);
        });
    }

    function createMiniCard(res, isRecommended, maxPrice) {
        const card = document.createElement('div');
        const cfg = getChainConfig(res.cadena);
        const progressPct = Math.round((res.total_viaje / maxPrice) * 100);
        const badgeHTML = res.type === 'completo'
            ? `<span class="badge-completo">✓ Lista completa</span>`
            : `<span class="badge-incompleto">⚠ Incompleto</span>`;

        card.className = `card-mini ${isRecommended ? 'recommended' : ''} ${res.type === 'incompleto' ? 'incompleto' : ''}`;
        card.style.setProperty('--chain-color', cfg.color);

        card.innerHTML = `
            <div class="card-top-bar" style="background:${cfg.color}20; border-bottom: 2px solid ${cfg.color}40;"></div>
            <div class="card-header-row">
                <div class="chain-logo-wrap">
                    ${getChainLogoHTML(res.cadena, 36)}
                </div>
                <div class="card-meta">
                    ${badgeHTML}
                    <h3 class="card-chain-name">${capitalize(res.cadena)}</h3>
                    <div class="dist"><i class="fa-solid fa-location-dot" style="color:${cfg.color};font-size:0.7rem"></i> ${res.distancia_km.toFixed(1)} km</div>
                </div>
                <div class="card-price-block">
                    <div class="price">$${res.total_viaje.toFixed(0)}</div>
                    <div class="dist">total</div>
                </div>
            </div>
            <div class="card-progress">
                <div class="progress-bar" style="width:${progressPct}%; background: linear-gradient(90deg, ${cfg.color}, #4ade80);"></div>
            </div>
            <div class="card-footer-hint">Toca para ver detalle →</div>
        `;
        if (isRecommended) {
            const star = document.createElement('div');
            star.className = 'recommended-badge';
            star.textContent = '★ Mejor opción';
            card.appendChild(star);
        }
        return card;
    }

    function openModal(res) {
        const cfg = getChainConfig(res.cadena);

        const listaProdHTML = res.productos_encontrados.map(p => `
            <div class="product-item">
                <span><small class="qty-badge">${p.cantidad}x</small> ${capitalize(p.producto)}</span>
                <div style="text-align:right">
                    <b style="color:#4ade80">$${p.precio_total.toFixed(2)}</b>
                    <div style="font-size:0.7rem; color:var(--text-muted);">u: $${p.precio_unitario.toFixed(2)}</div>
                </div>
            </div>
        `).join('');

        const faltantesHTML = res.productos_no_encontrados?.length ? `
            <div class="missing-items" style="margin-top:1rem; padding:1rem; background:rgba(248,113,113,0.1); border-radius:10px; border: 1px solid rgba(248,113,113,0.2);">
                <h4 style="color:#f87171; margin-bottom:0.5rem"><i class="fa-solid fa-circle-xmark"></i> No encontrados</h4>
                <div class="missing-list">${res.productos_no_encontrados.join(', ')}</div>
            </div>
        ` : '';

        modalBody.innerHTML = `
            <div class="modal-chain-header" style="border-bottom: 2px solid ${cfg.color}40; padding-bottom:1.5rem; margin-bottom:1.5rem;">
                <div style="display:flex; align-items:center; gap:1.2rem;">
                    <div style="width:60px;height:60px;border-radius:14px;overflow:hidden;background:white;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 4px 15px rgba(0,0,0,0.3)">
                        ${getChainLogoHTML(res.cadena, 56)}
                    </div>
                    <div>
                        <h2 style="font-size:1.8rem; margin-bottom:0.3rem; color:white">${capitalize(res.cadena)}</h2>
                        <p style="color:var(--text-muted); font-size:0.9rem"><i class="fa-solid fa-location-dot" style="color:${cfg.color}"></i> ${res.sucursal || res.cadena}</p>
                        <p style="font-size:0.75rem; opacity:0.6; margin-top:0.2rem">${res.direccion}</p>
                    </div>
                </div>
            </div>

            <div class="modal-grid">
                <div class="modal-products">
                    <h4 style="margin-bottom:1rem; color:#4ade80"><i class="fa-solid fa-check-double"></i> Productos encontrados (${res.productos_encontrados.length})</h4>
                    ${listaProdHTML}
                    ${faltantesHTML}
                </div>
                <div class="modal-summary">
                    <div class="summary-total-card" style="border-color: ${cfg.color}60; background: ${cfg.color}10;">
                        <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.3rem">Total estimado del viaje</div>
                        <div style="font-size:2.8rem; font-weight:900; color:#4ade80; line-height:1">$${res.total_viaje.toFixed(2)}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.3rem">incluyendo gasolina</div>
                    </div>
                    <div class="summary-breakdown">
                        <div class="breakdown-row">
                            <span>🛒 Subtotal productos</span>
                            <b>$${res.subtotal_productos.toFixed(2)}</b>
                        </div>
                        <div class="breakdown-row">
                            <span>⛽ Costo de gasolina</span>
                            <b>$${res.costo_gasolina.toFixed(2)}</b>
                        </div>
                        <div class="breakdown-row" style="border-top:1px solid var(--glass-border); padding-top:0.8rem; margin-top:0.3rem">
                            <span>📍 Distancia</span>
                            <b>${res.distancia_km.toFixed(1)} km</b>
                        </div>
                    </div>
                </div>
            </div>
        `;

        modalOverlay.classList.remove('hidden');
    }

    function capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }
});
