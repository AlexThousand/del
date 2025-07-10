from django.contrib import admin
from django.urls import include, path
from . import views
from django.views.generic import TemplateView





urlpatterns = [
    path("", views.index),
    path("api/zone", views.zones_all_geojson, name='zones_all_geojson'),
    path("api/patrol", views.patrols_all_json, name='get_patrol'),
    path("api/route-to-patrols/", views.route_to_patrols, name="route_to_patrols"),
]


