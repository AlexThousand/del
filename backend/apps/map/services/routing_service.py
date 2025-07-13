import requests
from django.contrib.gis.geos import Point
from ..models import Patrol


class RoutingService:
    def __init__(self, osrm_host="http://osrm:5000"):
        self.osrm_host = osrm_host
    
    def get_route(self, start_point, end_point):
        """
        Получает маршрут между двумя точками через OSRM.
        """
        print(f"start_point = {start_point}")
        print(f"end_point = {end_point}")
        
        url = f"{self.osrm_host}/route/v1/driving/{start_point.x},{start_point.y};{end_point.x},{end_point.y}"
        
        params = {
            "overview": "full",
            "geometries": "geojson",
            "alternatives": 3,
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
    
    def get_routes_to_patrols(self, lat, lon):
        """
        Получает маршруты от точки до всех патрулей.
        """
        start_point = Point(lon, lat, srid=4326)
        patrols = Patrol.objects.exclude(last_location__isnull=True).select_related('zone')
        results = []
        
        for patrol in patrols:
            route = self.get_route(start_point, patrol.last_location)
            
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