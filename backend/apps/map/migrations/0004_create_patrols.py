import random
from django.contrib.gis.geos import Point
from django.db import migrations


def create_patrols(apps, schema_editor):
    Zone = apps.get_model('map', 'Zone')
    Patrol = apps.get_model('map', 'Patrol')

    from apps.map.services import get_random_point_in_polygon

    for zone in Zone.objects.all():
        for i in range(5):
            point = get_random_point_in_polygon(zone.area)

            if not point:
                continue

            Patrol.objects.create(
                name=f'БАРЖА-{zone.id}{i + 1}',
                last_location=point,
                zone=zone
            )


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0003_patrol'),
    ]

    operations = [
        migrations.RunPython(create_patrols),
    ]
