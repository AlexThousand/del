import json
from ..models import Patrol


class PatrolService:
    def get_all_patrols_geojson(self):
        """Возвращает GeoJSON со всеми патрулями"""
        patrols = Patrol.objects.all()
        print(f"PatrolService: найдено {patrols.count()} патрулей")  # Отладочная информация
        features = []
        
        for patrol in patrols:
            if not patrol.last_location:
                print(f"PatrolService: патруль {patrol.id} без локации, пропускаем")  # Отладочная информация
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
        
        print(f"PatrolService: возвращаем {len(features)} features")  # Отладочная информация
        return geojson
    
    def find_closest_route_by_zone(self, zone_id, routes):
        """Находит ближайший маршрут в указанной зоне"""
        routes_in_zone = [r for r in routes if r.get("zone_id") == zone_id]
        
        if routes_in_zone:
            closest_in_zone = min(routes_in_zone, key=lambda r: r["distance_meters"])
            return closest_in_zone
        
        if routes:
            closest_any = min(routes, key=lambda r: r["distance_meters"])
            return closest_any
        
        return None
    
    def extract_patrol_name_and_distance(self, routes):
        """Извлекает имена патрулей и расстояния из маршрутов"""
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