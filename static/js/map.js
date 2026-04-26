// State
let map = null;
let scenarioId = null;
let shelters = [];
let dangerZones = [];
let markers = [];
let routeLayers = [];

// Initialize map centered on Bhubaneswar
function initMap() {
    map = L.map('map').setView([20.2961, 85.8245], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Click to get coordinates
    map.on('click', function(e) {
        setStatus(`Clicked: ${e.latlng.lat.toFixed(5)}, ${e.latlng.lng.toFixed(5)} — copy these into a zone/shelter`);
    });
}

// Status updater
function setStatus(msg, type = 'info') {
    const el = document.getElementById('status-text');
    el.textContent = msg;
    el.style.color = type === 'error' ? '#ff4757' : type === 'success' ? '#2ecc71' : '#aaa';
}

// Add shelter form
function addShelter() {
    const id = Date.now();
    const div = document.createElement('div');
    div.className = 'zone-card';
    div.id = `shelter-${id}`;
    div.innerHTML = `
        <div class="zone-card-header">
            <span>🏥 Shelter</span>
            <button onclick="removeCard('shelter-${id}')">✕</button>
        </div>
        <input type="text" placeholder="Name e.g. Kalinga Stadium" id="s-name-${id}"/>
        <input type="number" placeholder="Latitude e.g. 20.2700" id="s-lat-${id}" step="0.0001"/>
        <input type="number" placeholder="Longitude e.g. 85.8200" id="s-lon-${id}" step="0.0001"/>
        <input type="number" placeholder="Capacity e.g. 5000" id="s-cap-${id}"/>
    `;
    document.getElementById('shelters-list').appendChild(div);
}

// Add danger zone form
function addDangerZone() {
    const id = Date.now();
    const div = document.createElement('div');
    div.className = 'zone-card';
    div.id = `dz-${id}`;
    div.innerHTML = `
        <div class="zone-card-header">
            <span>🔴 Danger Zone</span>
            <button onclick="removeCard('dz-${id}')">✕</button>
        </div>
        <input type="text" placeholder="ID e.g. DZ1" id="dz-id-${id}"/>
        <input type="number" placeholder="Latitude e.g. 20.3100" id="dz-lat-${id}" step="0.0001"/>
        <input type="number" placeholder="Longitude e.g. 85.8100" id="dz-lon-${id}" step="0.0001"/>
        <input type="number" placeholder="Population e.g. 2000" id="dz-pop-${id}"/>
        <select id="dz-pri-${id}">
            <option value="1">Priority 1 — Critical (Hospital/Elderly)</option>
            <option value="2">Priority 2 — High (School/Dense Area)</option>
            <option value="3" selected>Priority 3 — Normal</option>
        </select>
    `;
    document.getElementById('dangerzones-list').appendChild(div);
}

function removeCard(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Collect shelter data from forms
function collectShelters() {
    const cards = document.querySelectorAll('[id^="shelter-"]');
    const result = [];
    cards.forEach(card => {
        const id = card.id.replace('shelter-', '');
        const name = document.getElementById(`s-name-${id}`)?.value;
        const lat = parseFloat(document.getElementById(`s-lat-${id}`)?.value);
        const lon = parseFloat(document.getElementById(`s-lon-${id}`)?.value);
        const cap = parseInt(document.getElementById(`s-cap-${id}`)?.value);
        if (name && lat && lon && cap) {
            result.push({ name, lat, lon, capacity: cap, current_occupancy: 0 });
        }
    });
    return result;
}

// Collect danger zone data from forms
function collectDangerZones() {
    const cards = document.querySelectorAll('[id^="dz-"]');
    const result = [];
    cards.forEach(card => {
        const id = card.id.replace('dz-', '');
        const dzId = document.getElementById(`dz-id-${id}`)?.value;
        const lat = parseFloat(document.getElementById(`dz-lat-${id}`)?.value);
        const lon = parseFloat(document.getElementById(`dz-lon-${id}`)?.value);
        const pop = parseInt(document.getElementById(`dz-pop-${id}`)?.value);
        const pri = parseInt(document.getElementById(`dz-pri-${id}`)?.value);
        if (dzId && lat && lon && pop) {
            result.push({ id: dzId, lat, lon, population: pop, priority: pri });
        }
    });
    return result;
}

// Create scenario
async function createScenario() {
    const name = document.getElementById('scenario-name').value;
    const city = document.getElementById('city-name').value;

    if (!name || !city) {
        setStatus('Please enter scenario name and city', 'error');
        return;
    }

    shelters = collectShelters();
    dangerZones = collectDangerZones();

    if (shelters.length === 0 || dangerZones.length === 0) {
        setStatus('Add at least one shelter and one danger zone', 'error');
        return;
    }

    setStatus('Creating scenario and loading city road network... (this may take 30-60 seconds)');

    try {
        const res = await fetch('/api/scenario/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, city, shelters, danger_zones: dangerZones })
        });

        const data = await res.json();

        if (!res.ok) {
            setStatus(`Error: ${data.detail}`, 'error');
            return;
        }

        scenarioId = data.scenario_id;
        setStatus(`Scenario created! ID: ${scenarioId}. Road network loaded.`, 'success');

        // Plot shelters and danger zones on map
        plotZones();

        document.getElementById('evacuate-btn').disabled = false;

    } catch (err) {
        setStatus(`Failed: ${err.message}`, 'error');
    }
}

// Plot zones on map
function plotZones() {
    // Clear existing markers
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    // Shelter markers
    shelters.forEach(s => {
        const marker = L.marker([s.lat, s.lon], {
            icon: L.divIcon({
                html: '🏥',
                className: '',
                iconSize: [24, 24]
            })
        }).addTo(map).bindPopup(`<b>${s.name}</b><br>Capacity: ${s.capacity}`);
        markers.push(marker);
    });

    // Danger zone markers
    dangerZones.forEach(dz => {
        const colors = { 1: '#ff4757', 2: '#ffa502', 3: '#eccc68' };
        const marker = L.circleMarker([dz.lat, dz.lon], {
            radius: 10,
            fillColor: colors[dz.priority] || '#eccc68',
            color: '#fff',
            weight: 2,
            fillOpacity: 0.9
        }).addTo(map).bindPopup(
            `<b>Danger Zone: ${dz.id}</b><br>Population: ${dz.population}<br>Priority: ${dz.priority}`
        );
        markers.push(marker);
    });

    // Fit map to markers
    const allCoords = [
        ...shelters.map(s => [s.lat, s.lon]),
        ...dangerZones.map(dz => [dz.lat, dz.lon])
    ];
    map.fitBounds(allCoords);
}

// Run evacuation
async function runEvacuation() {
    if (!scenarioId) {
        setStatus('Create a scenario first', 'error');
        return;
    }

    const algorithm = document.getElementById('algorithm').value;
    setStatus(`Running evacuation with ${algorithm.toUpperCase()}...`);

    // Clear previous routes
    routeLayers.forEach(l => map.removeLayer(l));
    routeLayers = [];

    try {
        const res = await fetch('/api/evacuate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_id: scenarioId, algorithm })
        });

        const data = await res.json();

        if (!res.ok) {
            setStatus(`Error: ${data.detail}`, 'error');
            return;
        }

        // Draw routes on map
        const colors = { 1: '#ff4757', 2: '#ffa502', 3: '#2ecc71' };
        data.routes.forEach(route => {
            if (route.path_coords.length > 1) {
                const color = colors[route.priority] || '#2ecc71';
                const line = L.polyline(route.path_coords, {
                    color,
                    weight: 3,
                    opacity: 0.8
                }).addTo(map).bindPopup(
                    `<b>${route.danger_zone_id} → ${route.shelter_name}</b><br>
                     Distance: ${route.distance}s<br>
                     Algorithm: ${route.algorithm}`
                );
                routeLayers.push(line);
            }
        });

        // Show results
        showResults(data);
        setStatus(`Evacuation complete! ${data.routes.length} routes computed.`, 'success');

    } catch (err) {
        setStatus(`Failed: ${err.message}`, 'error');
    }
}

// Show results panel
function showResults(data) {
    const resultsDiv = document.getElementById('results');
    const contentDiv = document.getElementById('results-content');
    resultsDiv.style.display = 'block';

    let html = `<p style="font-size:0.8rem;color:#aaa;margin-bottom:8px">
        Total evacuation time: <strong style="color:#2ecc71">${data.total_evacuation_time}s</strong>
    </p>`;

    // Routes
    data.routes.forEach(r => {
        html += `
        <div class="result-card priority-${r.priority}">
            <strong>${r.danger_zone_id} → ${r.shelter_name}</strong>
            <p>Distance: ${r.distance}s | Algorithm: ${r.algorithm}</p>
        </div>`;
    });

    // Shelter fill levels
    html += `<h3 style="font-size:0.78rem;color:#888;margin:10px 0 6px">Shelter Fill Levels</h3>`;
    Object.entries(data.shelter_fill_levels).forEach(([name, fill]) => {
        const cls = fill > 90 ? 'danger' : fill > 70 ? 'warning' : '';
        html += `
        <div style="margin-bottom:6px;font-size:0.78rem">
            <span>${name}: ${fill}%</span>
            <div class="fill-bar">
                <div class="fill-bar-inner ${cls}" style="width:${Math.min(fill,100)}%"></div>
            </div>
        </div>`;
    });

    contentDiv.innerHTML = html;
}

// Init on load
window.onload = initMap;