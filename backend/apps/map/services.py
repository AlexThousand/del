# apps/map/services.py
import json
import random
import requests
from django.contrib.gis.geos import Point

from .models import Patrol, Zone


def get_all_patrols_geojson():
    patrols = Patrol.objects.all()

    features = []

    for patrol in patrols:
        if not patrol.last_location:
            continue

        feature = {
            "type": "Feature",
            "geometry": json.loads(patrol.last_location.geojson),
            "properties": {
                "id": patrol.id,
                "name": patrol.name,
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    return geojson



def get_all_zones_geojson():
    zones = Zone.objects.all()
    features = []

    for zone in zones:
        feature = {
            "type": "Feature",
            "geometry": json.loads(zone.area.geojson),
            "properties": {
                "name": zone.name,
                "id": zone.id,
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return geojson


def get_random_point_in_polygon(polygon, attempts=100):
    min_x, min_y, max_x, max_y = polygon.extent

    for _ in range(attempts):
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)
        point = Point(x, y, srid=4326)

        if polygon.contains(point):
            return point

    return None


def get_route(start_point, end_point):
    OSRM_HOST = "http://osrm:5000"

    url = f"{OSRM_HOST}/route/v1/driving/{start_point.x},{start_point.y};{end_point.x},{end_point.y}"
    params = {
        "overview": "full",
        "geometries": "geojson"
    }
    try:
        response = requests.get(url, params=params, timeout=2)
        response.raise_for_status()
        data = response.json()
        if data.get("code") != "Ok" or not data.get("routes"):
            return None
        return data["routes"][0]
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching route: {e}")
        return None


def get_routes_to_patrols(lat, lon):
    start_point = Point(lon, lat, srid=4326)
    patrols = Patrol.objects.exclude(last_location__isnull=True).select_related('zone')
    results = []

    for patrol in patrols:
        route = get_route(start_point, patrol.last_location)
        if not route:
            continue
        results.append({
            "patrol_id": patrol.id,
            "patrol_name": patrol.name,
            "zone_id": patrol.zone.id,
            "distance_meters": route["distance"],
            "route_geometry": route["geometry"]
        })

    return results

def find_zone_by_point(lat: float, lon: float):
    point = Point(lon, lat, srid=4326)
    zone = Zone.objects.filter(area__contains=point).first()
    return zone

def find_closest_route_by_zone(zone_id: int, routes: list):
    routes_in_zone = [r for r in routes if r.get("zone_id") == zone_id]

    if routes_in_zone:
        closest_in_zone = min(routes_in_zone, key=lambda r: r["distance_meters"])
        return closest_in_zone

    if routes:
        closest_any = min(routes, key=lambda r: r["distance_meters"])
        return closest_any

    return None

def extract_patrol_name_and_distance(routes):
    return sorted(
        [
            {
                "patrol_name": route["patrol_name"],
                "distance_meters": route["distance_meters"]
            }
            for route in routes
        ],
        key=lambda r: r["distance_meters"]
    )