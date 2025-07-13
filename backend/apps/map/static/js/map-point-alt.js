document.addEventListener('DOMContentLoaded', () => {
    mapCore = new MapCore().init(false); // Не загружаем зоны и патрули
    const patrolListContainer = document.getElementById('patrol-list');

    const colors = [
        "red",
        "blue", 
        "orange",
        "green",
        "black"
    ];

    // Загружаем камеры
    mapCore.fetchJson('/static/js/mock-cameras.json')
        .then(results => {
            results.forEach(element => {
                L.marker([element['lat'], element['lng']], {icon: mapCore.icons.camera}).addTo(mapCore.map);
            });
        });

    // Загружаем точки и строим маршруты
    mapCore.fetchJson('/static/js/mock-points.json')
        .then(results => {
            // Добавляем маркеры точек
            results.forEach(element => {
                L.marker([element['lat'], element['lng']]).addTo(mapCore.map);
            });

            // Строим маршруты
            return mapCore.fetchJson(`${urls.route_points_alt}?array=${JSON.stringify(results)}`);
        })
        .then(data => {
            data.routes.forEach(route => {
                route.paths.forEach((path, index) => {
                    const latlngs = path.coordinates.map(coord => [coord[1], coord[0]]); // [lat, lng]

                    let offset, repeat, color;
                    if (index == 0) {
                        offset = index + "%";
                        repeat = "10%";
                    } else {
                        offset = index + "%";
                        repeat = "15%";
                    }

                    color = colors[index % colors.length];

                    var arrow = L.polyline(latlngs, { color: color }).addTo(mapCore.map);

                    var arrowHead = L.polylineDecorator(arrow, {
                        patterns: [
                            {offset: offset, repeat: repeat, symbol: L.Symbol.arrowHead({pixelSize: 15, polygon: false, pathOptions: {stroke: true, color:color}})}
                        ]
                    }).addTo(mapCore.map);
                });
            });
        })
        .catch(err => {
            console.error('Ошибка загрузки данных:', err);
        });
});