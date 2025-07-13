document.addEventListener('DOMContentLoaded', () => {
    mapCore = new MapCore().init(false); // Передаем false - НЕ загружаем зоны и патрули
    const patrolListContainer = document.getElementById('patrol-list');

    setupMapClickHandler();
});

function setupMapClickHandler() {
    const to_send = [];

    mapCore.map.on('click', async ({ latlng }) => {
        const { lat, lng } = latlng;

        const marker = L.marker([lat, lng]).addTo(mapCore.map);
        mapCore.state.clickMarkers.push(marker);
        
        try {
            to_send.length = 0;
            mapCore.state.clickMarkers.forEach(element => {
                to_send.push(element.getLatLng());
            });

            console.log(to_send);

            const data = await mapCore.fetchJson(`${urls.route_points}?array=${JSON.stringify(to_send)}`);

            data.routes.forEach(element => {
                console.log(element.geometry);
                L.geoJSON(element.geometry).addTo(mapCore.map);
            });

        } catch (err) {
            console.error('Ошибка запроса маршрута:', err);
        }
    });
}