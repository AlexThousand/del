from django.urls import path, include
from . import views, views_api

app_name = 'map'

page_patterns = [
    path('', views.index, name='index'),
    path('point/', views.point, name='point'),
    path('point_alt/', views.point_alt, name='point_alt'),
]

api_patterns = [
    path('zones/', views_api.zones_all_geojson, name='zones_list'),
    path('patrols/', views_api.patrols_all_json, name='patrols_list'),
    path('route-to-patrols/', views_api.route_to_patrols, name='routes_to_patrols'),
    path('route-points/', views_api.route_points, name='route_points'),
    path('route-points-alt/', views_api.route_points_alt, name='route_points_alt'),
]

urlpatterns = [
    *page_patterns,

    path('api/', include((api_patterns, 'api'))),
]