from typing import Any, Iterable
from django.db import models
from core.settings import BASE_DIR
from django.utils import timezone
from multiple_upload.models import Image
from espasa_info.models import CRM
from .apicon import MeliAPI

from django.db.models.signals import post_save
from django.dispatch import receiver

from .apicon import MeliAPI

# Create your models here.
def convertir_precio(obj):
    try:
        return int(obj.precio)
    except:
        try:
            return int(obj.precio.replace('$','').replace('.','').strip())
        except:
            return 0

def resp_ok(resp, name):
    if resp.status_code == 200 or resp.status_code == 402 or resp.status_code == 201:
        return True
    else:
        try:
            Errores.objects.create(name=f'{name} | {resp.status_code}',error=resp.json()).save()
        except:
            Errores.objects.create(name=f'{name} | {resp.status_code}',error=resp.text).save()
        return False

        
def resp_ok(resp, name):
    if resp.status_code == 200 or resp.status_code == 402 or resp.status_code == 201:
        return True
    else:
        try:
            Errores.objects.create(name=f'{name} | {resp.status_code}',error=resp.json()).save()
        except:
            Errores.objects.create(name=f'{name} | {resp.status_code}',error=resp.text).save()
        return False

class Errores(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    error = models.JSONField()
    

class MeliCon(models.Model):
    name = models.CharField(max_length = 30)
    app_id = models.CharField(max_length = 30)
    client_secret = models.CharField(max_length = 100)
    url = models.CharField(max_length = 100)
    code_tg = models.CharField(max_length = 100)
    access_token = models.CharField(max_length = 100)
    refresh_secret = models.CharField(max_length = 100)
    user_id = models.CharField(max_length=50, default='')
    
    def __str__(self) -> str:
        return self.name

class Atributo(models.Model):
    nombre = models.CharField(max_length = 30)
    id_att = models.CharField(max_length = 30)
    value = models.CharField(max_length = 40)
    
    def __str__(self) -> str:
        return self.nombre

class GrupoAtributos(models.Model):
    nombre = models.CharField(max_length = 100)
    atributos = models.ManyToManyField(Atributo, blank=True)
    pub_to_copy = models.CharField(max_length=50, help_text='Publicacion a copiar atributos, ej MLA12345', verbose_name='Copy ID')
    video_id = models.CharField(max_length=200, null=True,blank=True, default='')
    
    def __str__(self) -> str:
        return self.nombre

    
class GrupoImagenes(models.Model):
    codigo = models.CharField(max_length=10, default='')
    nombre = models.CharField(max_length = 100)
    imagenes = models.ManyToManyField(Image, blank=True)
    video = models.CharField(max_length=100, default='', null=True, blank=True)
    
    def __str__(self) -> str:
        return f'{self.codigo} | {self.nombre}'

    def delete(self,*args, **kwargs) -> tuple[int, dict[str, int]]:
        for item in self.imagenes.all():
            item.delete()
        
        super().delete()
    
    
class Modelo(models.Model):
    descripcion = models.CharField(max_length = 50,blank=True, null=True)
    anio = models.IntegerField(verbose_name = 'Año',blank=True, null=True)
    g_atributos = models.ForeignKey(GrupoAtributos, null = True, blank = True, on_delete = models.SET_NULL)
    g_imagenes = models.ForeignKey(GrupoImagenes, null = True, blank = True, on_delete = models.SET_NULL, verbose_name='Grp Img')
    categoria = models.CharField(max_length = 30, choices = {'silver': "Silver",'gold':'Gold','gold_premium':"Gold Premium"}, default='silver', null=True, blank=True)
    desc_meli = models.TextField(null=True, blank=True)
    precio = models.IntegerField(default = 0)
    espasa_db = models.ForeignKey(CRM, null=True, blank=True, on_delete=models.SET_NULL)
    pub_to_copy = models.CharField(max_length=50, help_text='Publicacion a copiar atributos, ej MLA12345', verbose_name='Copy ID', null=True, blank=True)
    video_id = models.CharField(max_length=200, null=True,blank=True, help_text='No tocar')
    
    def __str__(self) -> str:
        return f'{self.descripcion}'
    
    def save(self,*args,**kwargs):
        super().save()
        if self.g_atributos == None and self.pub_to_copy != None:
            api = MeliAPI(MeliCon.objects.get(name = 'API Dnogues'))
            g_att = GrupoAtributos.objects.create(nombre = self.descripcion)
            resp = api.consulta_pub(self.pub_to_copy)
            if resp_ok(resp, 'Consultar Atributos'):
                for at in resp.json()['attributes']:
                    try:
                        apend = Atributo.objects.get(id_att=at['id'],value=at['value_name'])
                    except:
                        apend = Atributo.objects.create(nombre = at['name'] ,id_att=at['id'],value=at['value_name']).save()     
                    apend = Atributo.objects.get(id_att=at['id'],value=at['value_name'])
                    g_att.atributos.add(apend)
                self.video_id = resp.json()['video_id'] 
            g_att.save()
            self.g_atributos = g_att
            super().save()               
        
        

class PubStats(models.Model):
    pub_id = models.CharField(max_length=100) 
    views = models.IntegerField(default = 0, verbose_name='vistas')
    clics_tel = models.IntegerField(default = 0, verbose_name='boton tel')

class Publicacion(models.Model):
    pub_id = models.CharField(max_length = 100)
    titulo = models.CharField(max_length = 100)
    desc = models.TextField()
    precio = models.CharField(max_length=50)
    categoria = models.CharField(max_length = 30)
    f_creado = models.DateTimeField(auto_now_add=True)
    f_actualizacion = models.DateTimeField(blank=True, null=True,default=timezone.now)
    activa = models.BooleanField(null = True, blank = True)
    modelo = models.ForeignKey(Modelo, on_delete = models.SET_NULL, null = True, blank = True)
    url = models.URLField(default='sinurl.com.ar')
    stats = models.ForeignKey(PubStats, on_delete=models.SET_NULL, null=True)
    sincronizado = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return self.pub_id
    
    def save(self, *args, **kwargs):
        precio = convertir_precio(self)
        self.precio = "$ {:,.0f}".format(precio).replace(",", ".")
        super().save()
        
