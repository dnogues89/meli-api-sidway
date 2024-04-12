# Generated by Django 5.0.3 on 2024-04-03 13:24

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meli_api', '0008_imagen_url_alter_imagen_imagen_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelo',
            name='desc_meli',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='modelo',
            name='imagenes',
        ),
        migrations.AddField(
            model_name='modelo',
            name='imagenes',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='meli_api.grupoimagenes'),
        ),
    ]
