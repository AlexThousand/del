import requests
import math
import json


class GraphHopperService:
    def __init__(self, base_url="http://graphhopper:8989"):
        self.base_url = base_url
        self.cameras = [
            {"lat": 46.958728886697386, "lng": 32.004493047248424},
            {"lat": 46.9661064663885, "lng": 31.980551445845467}
        ]
    
    def haversine(self, lat1, lon1, lat2, lon2):
        """Расстояние между двумя точками на сфере (в метрах)"""
        R = 6371000
        φ1, λ1 = math.radians(lat1), math.radians(lon1)
        φ2, λ2 = math.radians(lat2), math.radians(lon2)
        dφ = φ2 - φ1
        dλ = λ2 - λ1
        
        a = math.sin(dφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(dλ/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    def to_xy(self, lat, lon, lat0, lon0):
        """Перевод в локальные координаты в метрах"""
        R = 6371000
        x = math.radians(lon - lon0) * R * math.cos(math.radians(lat0))
        y = math.radians(lat - lat0) * R
        return x, y
    
    def point_to_segment_dist(self, lat, lon, lat1, lon1, lat2, lon2):
        """Расстояние от точки до отрезка на плоскости"""
        px, py = self.to_xy(lat, lon, lat, lon)
        x1, y1 = self.to_xy(lat1, lon1, lat, lon)
        x2, y2 = self.to_xy(lat2, lon2, lat, lon)
        
        dx, dy = x2 - x1, y2 - y1
        if dx == dy == 0:
            return math.hypot(px - x1, py - y1)
        
        t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(px - proj_x, py - proj_y)
    
    def is_crossing(self, camera, polyline, threshold_meters=20):
        """Проверяет, пересекает ли маршрут камеру"""
        lat0, lon0 = camera["lat"], camera["lng"]
        
        for i in range(len(polyline) - 1):
            lon1, lat1 = polyline[i]
            lon2, lat2 = polyline[i+1]
            
            dist = self.point_to_segment_dist(lat0, lon0, lat1, lon1, lat2, lon2)
            if dist <= threshold_meters:
                return True
        
        return False
    
    def route_crossing_camera(self, cameras, polyline, threshold_meters=20):
        """Проверяет, пересекает ли маршрут любую из камер"""
        for camera in cameras:
            if self.is_crossing(camera, polyline, threshold_meters):
                return True
        return False
    
    def calculate_azimuth(self, lat1, lon1, lat2, lon2):
        """Вычисляет азимут между двумя точками"""
        φ1 = math.radians(lat1)
        φ2 = math.radians(lat2)
        Δλ = math.radians(lon2 - lon1)
        
        x = math.sin(Δλ) * math.cos(φ2)
        y = math.cos(φ1) * math.sin(φ2) - math.sin(φ1) * math.cos(φ2) * math.cos(Δλ)
        
        θ = math.atan2(x, y)
        azimuth_deg = (math.degrees(θ) + 360) % 360
        
        return azimuth_deg
    
    def get_graphhopper_route(self, points, heading, max_paths=10, max_weight_factor=1.6, max_share_factor=0.9):
        """Получает маршрут через GraphHopper"""
        params = {
            "profile": "car",
            "locale": "en",
            "points_encoded": "false",
            "instructions": "false",
            "alternative_route.max_paths": max_paths,
            "alternative_route.max_weight_factor": max_weight_factor,
            "alternative_route.max_share_factor": max_share_factor,
            "algorithm": "alternative_route",
            "heading": heading,
            "ch.disable": "true"
        }
        
        query_parts = [f"{self.base_url}/route?"]
        
        for pt in points:
            lat = pt["lat"]
            lng = pt["lng"]
            query_parts.append(f"point={lat},{lng}&")
        
        for key, value in params.items():
            query_parts.append(f"{key}={value}&")
        
        url = "".join(query_parts).rstrip("&")
        
        try:
            response = requests.get(url, timeout=2)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching route: {e}")
            return None
    
    def parse_graphhopper_route(self, graphhopper_answer, points):
        """Парсит ответ GraphHopper"""
        time_real = points[1]['timestamp'] - points[0]['timestamp']
        
        results = {
            "points": points,
            "time_real": time_real,
            "paths": []
        }
        
        for path in graphhopper_answer['paths']:
            line = path['points']['coordinates']
            
            if self.route_crossing_camera(self.cameras, line):
                continue
            
            path['time'] = path['time'] / 1000
            
            row = {
                "distance": path['distance'],
                "time_presumable": path['time'],
                "time_sort": abs(path['time'] - time_real),
                "coordinates": path['points']['coordinates']
            }
            
            results['paths'].append(row)
        
        results['paths'] = sorted(results['paths'], key=lambda x: x["time_sort"])
        return results
    
    def pair_point_route(self, points):
        """Получает маршрут между двумя точками"""
        if len(points) != 2:
            return []
        
        azimuth = self.calculate_azimuth(
            points[0]['lat'], points[0]['lng'], 
            points[1]['lat'], points[1]['lng']
        )
        print(f"azimuth = {azimuth}")
        
        answer = self.get_graphhopper_route(points, azimuth)
        return self.parse_graphhopper_route(answer, points)
    
    def multi_point_route(self, points):
        """Получает маршруты между множественными точками"""
        route_list = []
        
        for i in range(len(points) - 1):
            points_pair = [points[i], points[i + 1]]
            route = self.pair_point_route(points_pair)
            route_list.append(route)
        
        return route_list
    
    def graphhopper_to_geojson(self, graphhopper_response_json):
        """Конвертирует ответ GraphHopper в GeoJSON"""
        features = []
        
        for path in graphhopper_response_json.get('paths', []):
            coords = path.get('points', {}).get('coordinates', [])
            
            instructions = []
            for instr in path.get('instructions', []):
                text = instr.get('text')
                if text:
                    instructions.append(text)
            
            feature = {
                "type": "Feature",
                "properties": {
                    "distance_m": path.get('distance'),
                    "time_ms": path.get('time'),
                    "weight": path.get('weight'),
                    "instructions": instructions
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                }
            }
            features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return geojson
    
    def get_graphhopper_route_simple(self, points):
        """Упрощенная версия получения маршрута через GraphHopper"""
        params = {
            "profile": "car",
            "locale": "en",
            "points_encoded": "false",
            "details": "road_class",
            "alternative_route.max_paths": "10",
            "alternative_route.max_weight_factor": "1.5",
            "alternative_route.max_share_factor": "1",
            "algorithm": "alternative_route"
        }
        
        query_parts = [f"{self.base_url}/route?"]
        
        for pt in points:
            lat = pt["lat"]
            lng = pt["lng"]
            query_parts.append(f"point={lat},{lng}&")
        
        for key, value in params.items():
            query_parts.append(f"{key}={value}&")
        
        url = "".join(query_parts).rstrip("&")
        
        try:
            response = requests.get(url, timeout=2)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching route: {e}")
            return None