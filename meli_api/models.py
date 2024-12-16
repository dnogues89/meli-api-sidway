from typing import Any, Iterable
from django.db import models
from core.settings import BASE_DIR
from django.utils import timezone
from multiple_upload.models import Image
from espasa_info.models import CRM
from .apicon import MeliAPI
from usuarios.models import Cuenta

from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from .apicon import MeliAPI

# Create your models here.
def convertir_precio2(precio):
    try:
        return int(precio)
    except:
        try:
            return int(precio.replace('$','').replace('.','').strip())
        except:
            return 0


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
        return f'{self.id} | {self.nombre} | {self.value}'

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
        
class Portadas(models.Model):
    codigo = models.CharField(max_length=10, default='')
    nombre = models.CharField(max_length = 100)
    imagenes = models.ManyToManyField(Image, blank=True)

    def __str__(self) -> str:
        return f'{self.codigo} | {self.nombre}'

    def delete(self,*args, **kwargs) -> tuple[int, dict[str, int]]:
        for item in self.imagenes.all():
            item.delete()
        
        super().delete()
    
class Modelo(models.Model):
    marca = models.CharField(max_length=100, default='', null=True, blank=True)
    descripcion = models.CharField(max_length = 50,blank=True, null=True)
    anio = models.IntegerField(verbose_name = 'Año',blank=True, null=True)
    g_atributos = models.ForeignKey(GrupoAtributos, null = True, blank = True, on_delete = models.SET_NULL)
    portadas = models.ForeignKey(Portadas, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Portadas')
    g_imagenes = models.ForeignKey(GrupoImagenes, null = True, blank = True, on_delete = models.SET_NULL, verbose_name='Grp Img')
    categoria = models.CharField(max_length = 30, choices = {'silver': "Silver",'gold':'Gold','gold_premium':"Gold Premium"}, default='gold_premium', null=True, blank=True)
    desc_meli = models.TextField(null=True, blank=True)
    precio = models.IntegerField(default = 0)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    espasa_db = models.ForeignKey(CRM, null=True, blank=True, on_delete=models.SET_NULL)
    pub_to_copy = models.CharField(max_length=50, help_text='Publicacion a copiar atributos, ej MLA12345', verbose_name='Copy ID', null=True, blank=True)
    video_id = models.CharField(max_length=200, null=True,blank=True, help_text='No tocar')
    cantidad = models.IntegerField(default=1, verbose_name='A Publicar')
    search_page = models.CharField(max_length= 200, blank=True, help_text='Casillero para identificar las busquedas', default='')

    
    def __str__(self) -> str:
        return f'{self.descripcion}'
    
    def save(self,*args,**kwargs):
        super().save()
        marca = self.descripcion.split(' ')[0].lower()
        if marca == 'renegade' or marca == 'compass' or marca == 'commander':
            self.marca = 'JEEP'
        else:
            self.marca = 'RAM'
        #Agregamos atributos a la publicacion haciendo una creacion de grupo de atributos
        if self.g_atributos == None and self.pub_to_copy != None:
            api = MeliAPI(Cuenta.objects.all()[0])
            g_att = GrupoAtributos.objects.create(nombre = self.descripcion)
            g_att.save()
            resp = api.consulta_pub(self.pub_to_copy)
            if resp_ok(resp, 'Consultar Atributos'):
                self.video_id = resp.json()['video_id'] 
                for at in resp.json()['attributes']:
                    apend = Atributo.objects.filter(id_att=at['id']).filter(value=at['value_name'])
                    if len(apend) == 0:
                        apend = Atributo.objects.create(nombre = at['name'] ,id_att=at['id'],value=at['value_name'])
                        apend.save()    
                    apend = Atributo.objects.filter(id_att=at['id'],value=at['value_name'])[0]
                    g_att.atributos.add(apend)
                    print(g_att.atributos.count())
            g_att.save()
            self.g_atributos = g_att
            my = Atributo.objects.filter(id_att = 'VEHICLE_YEAR')
            for item in my:
                item.value = timezone.now().year
                item.save()
                
        super().save()
        
        

class PubStats(models.Model):
    pub_id = models.CharField(max_length=100) 
    views = models.IntegerField(default = 0, verbose_name='vistas')
    clics_tel = models.IntegerField(default = 0, verbose_name='boton tel')
    ubicacion = models.CharField(max_length=100, blank=True, null=True, default='')
    
    
    def __str__(self) -> str:
        return self.pub_id

class Publicacion(models.Model):
    pub_id = models.CharField(max_length = 100)
    titulo = models.CharField(max_length = 100)
    desc = models.TextField(null=True, blank=True)
    precio = models.CharField(max_length=50)
    categoria = models.CharField(max_length = 30)
    f_creado = models.DateTimeField(auto_now_add=True)
    f_actualizacion = models.DateTimeField(blank=True, null=True,default=timezone.now)
    activa = models.BooleanField(null = True, blank = True)
    modelo = models.ForeignKey(Modelo, on_delete = models.SET_NULL, null = True, blank = True)
    url = models.URLField(default='sinurl.com.ar')
    stats = models.ForeignKey(PubStats, on_delete=models.CASCADE, null=True)
    sincronizado = models.BooleanField(default=False)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    banner = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return self.pub_id
    

    
    def save(self, *args, **kwargs):
        precio = convertir_precio(self)
        self.precio = "${:,.0f}".format(precio).replace(",", ".")
        try:
            old = Publicacion.objects.get(pk=self.pk)
            if self.precio != old.precio:
                self.sincronizado = False
        except:
            pass
        super().save()
        
@receiver(post_delete, sender=Publicacion)
def delete_pubstats(sender, instance, **kwargs):
    if instance.stats:
        instance.stats.delete()