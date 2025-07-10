from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Zone

from django.http import JsonResponse
from .services import get_all_zones_geojson, get_route, get_routes_to_patrols, find_zone_by_point, find_closest_route_by_zone, extract_patrol_name_and_distance, get_all_patrols_geojson


@login_required
def index(request):
    return render(request, "main.html")


#API
@login_required
def zones_all_geojson(request):
    geojson = get_all_zones_geojson()
    return JsonResponse(geojson)

@login_required
def patrols_all_json(request):
    geojson = get_all_patrols_geojson()
    return JsonResponse(geojson)

@login_required
def route_to_patrols(request):
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid or missing lat/lon"}, status=400)

    routes = get_routes_to_patrols(lat, lon)
    target_zone = find_zone_by_point(lat, lon)

    if not target_zone:
        return JsonResponse({"error": "Zone not founded"}, status=406)

    best_route = find_closest_route_by_zone(target_zone.id, routes)
    patrol_distance = extract_patrol_name_and_distance(routes)

    return JsonResponse({"best_route": best_route, "patrols": patrol_distance})