from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from .models import CRM
from .espasa_conn import EspasaDataBase
from meli_api.models import Modelo
from unfold.admin import ModelAdmin

def model_text(text):
    return str(text).replace('(','').replace(')','').replace("'","")

# Register your models here.
@admin.register(CRM)
class CRMAdmin(ModelAdmin):
    list_display = ['codigo','desc','stock','precio_tx','ofertas','oferta_min']