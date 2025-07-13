import json
from django.contrib.gis.geos import Point
from ..models import Zone


class ZoneService:
    def get_all_zones_geojson(self):
        """Возвращает GeoJSON со всеми зонами"""
        zones = Zone.objects.all()
        print(f"ZoneService: найдено {zones.count()} зон")  # Отладочная информация
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
        
        print(f"ZoneService: возвращаем {len(features)} features")  # Отладочная информация
        return geojson
    
    def find_zone_by_point(self, lat, lon):
        """Находит зону по координатам точки"""
        point = Point(lon, lat, srid=4326)
        zone = Zone.objects.filter(area__contains=point).first()
        return zone