from django.db import migrations
from django.contrib.gis.geos import GEOSGeometry
import os
import json
from pathlib import Path

def load_zones_from_geojson(apps, schema_editor):
    Zone = apps.get_model("map", "Zone")

    base_dir = Path(__file__).resolve().parent
    geojson_path = base_dir.parent / 'data' / 'regions.geojson'

    with geojson_path.open(encoding='utf-8') as f:
        data = json.load(f)

    for i, feature in enumerate(data['features'], start=1):
        name = f'Зона обслуговування №{i}'
        geom = GEOSGeometry(json.dumps(feature['geometry']), srid=4326)
        Zone.objects.create(name=name, area=geom)

class Migration(migrations.Migration):

    dependencies = [
        ('map', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(load_zones_from_geojson),
    ]
