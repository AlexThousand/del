document.addEventListener('DOMContentLoaded', () => {
    mapCore = new MapCore().init(true); // Загружаем зоны и патрули
    const patrolListContainer = document.getElementById('patrol-list');

    setupMapClickHandler();
});

function setupMapClickHandler() {
    mapCore.map.on('click', async ({ latlng }) => {
        const { lat, lng } = latlng;

        if (mapCore.state.clickMarker) mapCore.state.clickMarker.remove();
        mapCore.state.clickMarker = L.marker([lat, lng]).addTo(mapCore.map);

        try {
            const data = await mapCore.fetchJson(`${urls.route}?lat=${lat}&lon=${lng}`);

            mapCore.clearLayer(mapCore.state.currentRouteLayer);
            
            if (!data.best_route?.route_geometry) {
                console.warn('Нет данных маршрута для отрисовки');
                return;
            }

            mapCore.state.currentRouteLayer = L.geoJSON(data.best_route.route_geometry, {
                style: { color: 'red', weight: 5, opacity: 0.8 }
            }).addTo(mapCore.map);

            const bounds = mapCore.state.currentRouteLayer.getBounds();
            if (bounds.isValid()) mapCore.map.fitBounds(bounds, { padding: [50, 50] });

            mapCore.highlightBestPatrol(data.best_route.patrol_id);
            mapCore.renderPatrolList(data.patrols, document.getElementById('patrol-list'));

        } catch (err) {
            console.error('Ошибка запроса маршрута:', err);
        }
    });
} 