// Базовые функции для работы с картой
class MapCore {
    constructor(config) {
        this.config = config || {};
        this.map = null;
        this.state = {
            patrolMarkers: new Map(),
            activePatrolMarker: null,
            currentRouteLayer: null,
            clickMarkers: []
        };
        this.icons = {
            default: this.createIcon('/static/images/car-icon.png'),
            highlight: this.createIcon('/static/images/car-icon-red.png'),
            camera: this.createIcon('/static/images/camera.png')
        };
    }

    init(loadZonesAndPatrols = false) {
        this.map = this.initMap(this.config.center || [46.9623294952775, 32.00096573612804], this.config.zoom || 13);
        
        // Загружаем зоны и патрули только если явно указано
        if (loadZonesAndPatrols) {
            this.loadZones();
            this.loadPatrols();
        }
        
        return this;
    }

    initMap(center, zoom) {
        const map = L.map('map').setView(center, zoom);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        return map;
    }

    createIcon(url) {
        return L.icon({
            iconUrl: url,
            iconSize: [32, 37],
            iconAnchor: [16, 37],
            popupAnchor: [0, -28]
        });
    }

    clearLayer(layer) {
        if (layer) layer.remove();
    }

    async fetchJson(url) {
        const response = await fetch(url, {
            credentials: 'same-origin', // Включаем cookies для аутентификации
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    }

    loadZones() {
        console.log('Загружаем зоны из:', urls.zones);
        this.fetchJson(urls.zones)
            .then(geojson => {
                console.log('Получены зоны:', geojson);
                L.geoJSON(geojson).addTo(this.map);
            })
            .catch(err => console.error('Ошибка загрузки зон:', err));
    }

    loadPatrols() {
        console.log('Загружаем патрули из:', urls.patrols);
        this.fetchJson(urls.patrols)
            .then(geojson => {
                console.log('Получены патрули:', geojson);
                L.geoJSON(geojson, {
                    pointToLayer: (feature, latlng) => {
                        const marker = L.marker(latlng, { icon: this.icons.default });
                        const patrolId = feature.properties?.id;
                        if (patrolId !== undefined) this.state.patrolMarkers.set(patrolId, marker);
                        return marker;
                    },
                    onEachFeature: (feature, layer) => {
                        if (feature.properties?.name) {
                            layer.bindPopup(feature.properties.name);
                        }
                    }
                }).addTo(this.map);
            })
            .catch(err => console.error('Ошибка загрузки патрулей:', err));
    }

    highlightBestPatrol(patrolId) {
        if (this.state.activePatrolMarker) {
            this.state.activePatrolMarker.setIcon(this.icons.default);
            this.state.activePatrolMarker = null;
        }

        if (patrolId && this.state.patrolMarkers.has(patrolId)) {
            const marker = this.state.patrolMarkers.get(patrolId);
            marker.setIcon(this.icons.highlight);
            this.state.activePatrolMarker = marker;
        }
    }

    renderPatrolList(patrols, container) {
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
}

// Глобальный экземпляр
let mapCore; 