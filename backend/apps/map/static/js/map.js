document.addEventListener('DOMContentLoaded', () => {
    const map = initMap([46.9623294952775, 32.00096573612804], 13);
    const patrolListContainer = document.getElementById('patrol-list');


    const icons = {
        default: createIcon('/static/images/car-icon.png'),
        highlight: createIcon('/static/images/car-icon-red.png')
    };

    const state = {
        patrolMarkers: new Map(),
        activePatrolMarker: null,
        currentRouteLayer: null,
        clickMarker: null
    };

    setupMapClickHandler(map, urls.route, state, icons, patrolListContainer);
    loadZones(urls.zones, map);
    loadPatrols(urls.patrols, map, state.patrolMarkers, icons.default);
});

function initMap(center, zoom) {
    const map = L.map('map').setView(center, zoom);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    return map;
}

function createIcon(url) {
    return L.icon({
        iconUrl: url,
        iconSize: [32, 37],
        iconAnchor: [16, 37],
        popupAnchor: [0, -28]
    });
}

function setupMapClickHandler(map, routeUrl, state, icons, listContainer) {
    map.on('click', async ({ latlng }) => {
        const { lat, lng } = latlng;

        if (state.clickMarker) state.clickMarker.remove();
        state.clickMarker = L.marker([lat, lng]).addTo(map);

        try {
            const data = await fetchJson(`${routeUrl}?lat=${lat}&lon=${lng}`);

            clearLayer(state.currentRouteLayer);
            
            if (!data.best_route?.route_geometry) {
                console.warn('Нет данных маршрута для отрисовки');
                return;
            }

            state.currentRouteLayer = L.geoJSON(data.best_route.route_geometry, {
                style: { color: 'red', weight: 5, opacity: 0.8 }
            }).addTo(map);

            const bounds = state.currentRouteLayer.getBounds();
            if (bounds.isValid()) map.fitBounds(bounds, { padding: [50, 50] });

            highlightBestPatrol(data.best_route.patrol_id, state, icons);
            renderPatrolList(data.patrols, listContainer);

        } catch (err) {
            console.error('Ошибка запроса маршрута:', err);
        }
    });
}

function clearLayer(layer) {
    if (layer) layer.remove();
}

function highlightBestPatrol(patrolId, state, icons) {
    if (state.activePatrolMarker) {
        state.activePatrolMarker.setIcon(icons.default);
        state.activePatrolMarker = null;
    }

    if (patrolId && state.patrolMarkers.has(patrolId)) {
        const marker = state.patrolMarkers.get(patrolId);
        marker.setIcon(icons.highlight);
        state.activePatrolMarker = marker;
    }
}

function loadZones(url, map) {
    fetchJson(url)
        .then(geojson => L.geoJSON(geojson).addTo(map))
        .catch(err => console.error('Ошибка загрузки зон:', err));
}

function loadPatrols(url, map, markerMap, defaultIcon) {
    fetchJson(url)
        .then(geojson => {
            L.geoJSON(geojson, {
                pointToLayer: (feature, latlng) => {
                    const marker = L.marker(latlng, { icon: defaultIcon });
                    const patrolId = feature.properties?.id;
                    if (patrolId !== undefined) markerMap.set(patrolId, marker);
                    return marker;
                },
                onEachFeature: (feature, layer) => {
                    if (feature.properties?.name) {
                        layer.bindPopup(feature.properties.name);
                    }
                }
            }).addTo(map);
        })
        .catch(err => console.error('Ошибка загрузки патрулей:', err));
}

function renderPatrolList(patrols, container) {
    if (!Array.isArray(patrols) || patrols.length === 0) {
        container.innerHTML = '<p>Нет доступных патрулей</p>';
        return;
    }

    const table = document.createElement('table');
    table.className = 'table table-bordered table-sm';
    table.innerHTML = `
        <thead><tr><th>Позывной</th><th>Дистанция (м)</th></tr></thead>
        <tbody>
            ${patrols.map(p => `<tr><td>${p.patrol_name}</td><td>${Math.round(p.distance_meters)}</td></tr>`).join('')}
        </tbody>
    `;
    container.innerHTML = '';
    container.appendChild(table);
}

function fetchJson(url) {
    return fetch(url).then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    });
}