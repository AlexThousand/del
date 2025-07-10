from django.contrib.gis.db import models as gis_models
from django.db import models

class Zone(gis_models.Model):
    name = models.CharField(max_length=50)
    area = gis_models.PolygonField(srid=4326)  # SRID 4326 — стандарт для GPS (WGS84)

    def __str__(self):
        return self.name

class Patrol(gis_models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='patrols')
    name = models.CharField(max_length=50)
    last_location = gis_models.PointField(srid=4326, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.zone.name})"