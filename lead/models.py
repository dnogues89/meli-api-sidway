from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class Lead(models.Model):
    lead_id = models.CharField(max_length=100)
    item_id = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100, default='Sin modelo')
    familia = models.CharField(max_length=100, default='Sin definir')
    origen = models.CharField(max_length=1000, default='Desconocido')
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    date = models.DateTimeField(null=True, blank=True)
    to_crm = models.BooleanField(default=False)
    contactos = models.IntegerField(default=0)
    
class Estadisticas(models.Model):
    cuenta = models.CharField(max_length=100,default='Estadisticas LIMA')
    hoy = models.IntegerField(default=0)
    ayer = models.IntegerField(default=0)
    ultimos_3_dias = models.IntegerField(default=0)
    x_dia_30_dias = models.FloatField(default=0.0)
    total = models.IntegerField(default=0)

    def actualizar_estadisticas(self):
        ahora = timezone.now()
        hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        ayer_inicio = hoy_inicio - timedelta(days=1)
        tres_dias_inicio = hoy_inicio - timedelta(days=3)
        treinta_dias_inicio = hoy_inicio - timedelta(days=30)

        self.hoy = Lead.objects.filter(date__gte=hoy_inicio).count()
        self.ayer = Lead.objects.filter(date__gte=ayer_inicio, date__lt=hoy_inicio).count()
        self.ultimos_3_dias = Lead.objects.filter(date__gte=tres_dias_inicio).count()
        self.x_dia_30_dias = int(Lead.objects.filter(date__gte=treinta_dias_inicio).count() / 30)
        self.total = Lead.objects.all().count()
        self.save()

    def __str__(self):
        return "Estadisticas"