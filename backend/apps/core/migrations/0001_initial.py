from django.db import migrations
from pathlib import Path
from django.contrib.auth.models import User

def load_zones_from_geojson(apps, schema_editor):
    user = User.objects.create_user("demo", "demo@demo.com", "demo")
    user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]
    operations = [
        migrations.RunPython(load_zones_from_geojson),
    ]