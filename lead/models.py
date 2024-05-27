from django.db import models
from meli_api.models import Publicacion

# Create your models here.
class Lead(models.Model):
    lead_id = models.CharField(max_length=100)
    item_id = models.ForeignKey(Publicacion, null=True, on_delete=models.SET_NULL, blank=True)
    modelo = models.CharField(max_length=100, default='Sin modelo')
    origen = models.CharField(max_length=1000, default='Desconocido')
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    date = models.DateTimeField(null=True, blank=True)
    to_crm = models.BooleanField(default=False)
    contactos = models.IntegerField(default=0)