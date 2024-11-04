from django.db import models
from django.utils import timezone
from datetime import timedelta
from usuarios.models import Cuenta
from espasa_info.espasa_conn import EspasaDataBase
from django.conf import settings

# Create your models here.

class Usado(models.Model):
    id_sioma = models.CharField(max_length=100)
    compra = models.DateField()
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    anio = models.CharField(max_length=10)
    cerokm = models.BooleanField()
    venta = models.DateField(null=True, blank=True)
    CHOICES = {
        'Prenda':'Prenda',
        'Cash':'Cash'
    }
    tipo_compra = models.CharField(max_length=100,choices=CHOICES)
    tipo_acreedor = models.CharField(max_length=100, null=True,blank=True)
    acreedor = models.CharField(max_length=100, null=True,blank=True)
    
    
class Cuit(models.Model):
    nombre = models.CharField(max_length=100, null=True,blank=True)
    localidad = models.CharField(max_length=100, null=True, blank=True)
    dni = models.CharField(max_length=100, blank=True, null=True)
    cuil = models.CharField(max_length=100, blank=True, null=True)
    usados = models.ManyToManyField(Usado, blank=True)


class CuitInfo(models.Model):
    cuit=models.CharField(max_length=50)
    marca=models.CharField(max_length=100)
    modelo=models.CharField(max_length=100)
    tipo=models.CharField(max_length=100)
    fecha_ultimo_pat=models.DateField()
    provincia=models.CharField(max_length=50)
    cliente=models.BooleanField(max_length=50)
    usados = models.ManyToManyField(Usado, blank=True)
    
    
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
    cuenta = models.ForeignKey(Cuenta, on_delete=models.SET_NULL, null=True)
    cuit = models.CharField(max_length=100,default=0)
    cuit_info = models.ForeignKey(CuitInfo, on_delete=models.SET_NULL, default=None, null=True)
    siomaa_info = models.ForeignKey(Cuit, on_delete=models.SET_NULL, default =None, null=True)
    
    def save(self, *args, **kwargs):
        if self.cuit_info == None and self.cuit != 0:
            conn = EspasaDataBase()
            info = conn.get_info_by_cuit(self.cuit)
            print(info)
            if info:
                settings.USE_TZ = False
                cuit_info = CuitInfo.objects.create(cuit=self.cuit, marca=info['marca'], modelo=info['modelo'], tipo=info['tipo'], fecha_ultimo_pat=info['fecha_ultimo_pat'], provincia=info['provincia'], cliente=info['cliente'])
                cuit_info.save()
                self.cuit_info = cuit_info
                settings.USE_TZ = True
    
        super().save(*args, **kwargs)
    
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

