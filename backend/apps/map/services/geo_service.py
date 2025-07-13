import random
from django.contrib.gis.geos import Point


class GeoService:
    def get_random_point_in_polygon(self, polygon, attempts=100):
        """Генерирует случайную точку внутри полигона"""
        min_x, min_y, max_x, max_y = polygon.extent
        
        for _ in range(attempts):
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            point = Point(x, y, srid=4326)
            
            if polygon.contains(point):
                return point
        
        return None