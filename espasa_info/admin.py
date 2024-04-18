from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from .models import CRM
from .espasa_conn import EspasaDataBase

def model_text(text):
    return str(text).replace('(','').replace(')','').replace("'","")

# Register your models here.
@admin.register(CRM)
class CRMAdmin(admin.ModelAdmin):
    list_display = ['codigo','modelo','stock']
    
    def get_queryset(self,request):
        qs = super().get_queryset(request)
        conn = EspasaDataBase()
        for item in conn.get_info():
            try:
                obj = CRM.objects.get(codigo = item[0])
                obj.modelo = str(item[1])
                obj.familia = str(item[2])
                obj.precio_lista = str(item[3])
                obj.impuestos_internos = str(item[4])
                obj.precio_tx = str(item[5])
                obj.stock = str(item[6])
                obj.ofertas = str(item[7])
                obj.oferta_min = str(item[8])
                obj.oferta_max = str(item[9])
                obj.save()
            except:
                    
                obj = CRM.objects.create(
                    codigo = item[0],
                    modelo = item[1],
                    familia = item[2],
                    precio_lista = item[3],
                    impuestos_internos = item[4],
                    precio_tx = item[5],
                    stock = item[6],
                    ofertas = item[7],
                    oferta_min = item[8],
                    oferta_max = item[9]
                ).save()
            
        return qs