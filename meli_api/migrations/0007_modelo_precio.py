# Generated by Django 5.0.3 on 2024-04-03 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meli_api', '0006_melicon_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelo',
            name='precio',
            field=models.IntegerField(default=0),
        ),
    ]
