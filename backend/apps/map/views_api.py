import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point

from .services.routing_service import RoutingService
from .services.graphhopper_service import GraphHopperService
from .services.patrol_service import PatrolService
from .services.zone_service import ZoneService


routing_service = RoutingService()
graphhopper_service = GraphHopperService()
patrol_service = PatrolService()
zone_service = ZoneService()


# @login_required  # Временно отключаем для тестирования
def zones_all_geojson(request):
    """
    Возвращает GeoJSON со всеми зонами.
    """
    geojson = zone_service.get_all_zones_geojson()
    print(f"API zones: {geojson}")  # Отладочная информация
    return JsonResponse(geojson)


# @login_required  # Временно отключаем для тестирования
def patrols_all_json(request):
    """
    Возвращает GeoJSON со всеми патрулями.
    """
    geojson = patrol_service.get_all_patrols_geojson()
    print(f"API patrols: {geojson}")  # Отладочная информация
    return JsonResponse(geojson)


@login_required
def route_to_patrols(request):
    """
    Получает lat и lon из GET параметров, возвращает лучший маршрут и список патрулей.
    """
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid or missing lat/lon"}, status=400)

    routes = routing_service.get_routes_to_patrols(lat, lon)
    target_zone = zone_service.find_zone_by_point(lat, lon)

    if not target_zone:
        return JsonResponse({"error": "Zone not found"}, status=406)

    best_route = patrol_service.find_closest_route_by_zone(target_zone.id, routes)
    patrol_distance = patrol_service.extract_patrol_name_and_distance(routes)

    return JsonResponse({"best_route": best_route, "patrols": patrol_distance})


@login_required
def route_points(request):
    """
    Получает массив точек (GET параметр 'array' в JSON), возвращает маршруты между ними.
    """
    array_json = request.GET.get("array")

    if not array_json:
        return JsonResponse({"error": "Missing 'array' parameter"}, status=400)

    try:
        array = json.loads(array_json)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in 'array'"}, status=400)

    if len(array) < 2:
        return JsonResponse({"error": "Need at least two points"}, status=400)

    route_list = []
    for i in range(len(array) - 1):
        start = array[i]
        end = array[i + 1]

        start_point = Point(start['lng'], start['lat'], srid=4326)
        end_point = Point(end['lng'], end['lat'], srid=4326)

        route = routing_service.get_route(start_point, end_point)
        route_list.append(route)

    return JsonResponse({"routes": route_list})


@login_required
def route_points_alt(request):
    """
    Альтернативный маршрут для массива точек (GET параметр 'array' в JSON).
    """
    array_json = request.GET.get("array")

    if not array_json:
        return JsonResponse({"error": "Missing 'array' parameter"}, status=400)

    try:
        array = json.loads(array_json)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in 'array'"}, status=400)

    if len(array) < 2:
        return JsonResponse({"error": "Need at least two points"}, status=400)

    routes = graphhopper_service.multi_point_route(array)

    return JsonResponse({"routes": routes})
