from django.db import models
from meli_api.models import Publicacion

# Create your models here.
class Lead(models.Model):
    lead_id = models.CharField(max_length=100)
    item_id = models.ForeignKey(Publicacion, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    date = models.DateTimeField(auto_created=True)
    to_crm = models.CharField(max_length=100)