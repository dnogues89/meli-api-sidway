from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from .models import *
from .publicaciones import ArmarPublicacion
from .apicon import MeliAPI
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse


# api = MeliAPI(MeliCon.objects.get(name = 'API Dnogues'))

def resp_ok(resp, name):
    if resp.status_code == 200 or resp.status_code == 402 or resp.status_code == 201:
        return True
    else:
        try:
            Errores.objects.create(name=f'{name} | {resp.status_code}',error=resp.json()).save()
        except:
            Errores.objects.create(name=f'{name} | {resp.status_code}',error=resp.text).save()
        return False


       
# Register your models here.
@admin.register(Errores)
class ErroresAdmin(admin.ModelAdmin):
    list_display = ('name','fecha','error')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)

@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display=('titulo_short','pub_id', 'cat','precio', 'creado','actualizado','activa','visualizaciones','clics_tel','ver','sincronizado')
    list_editable =('precio',)
    actions = ('pausar','eliminar','actualizar_precio','sinconizar_meli')
    search_fields = ('titulo', 'pub_id','categoria','precio','activa')
    
    @admin.action(description='Sincronizar pubs con Meli')
    def sinconizar_meli(self,request,obj):
        api = MeliAPI(MeliCon.objects.get(name = 'API Dnogues'))
        resp = api.items_by_id(MeliCon.objects.get(name = 'API Dnogues').user_id)
        if resp_ok(resp,'Buscando Publicaciones'):
            pubs_meli = resp.json()['results']
            pubs_django = [obj.pub_id for obj in  Publicacion.objects.all()]
            for obj in set(pubs_meli) - set(pubs_django):
                resp = api.consulta_pub(obj)
                if resp_ok(resp,'Consulta publicacion'):
                    resp = resp.json()
                    Publicacion.objects.create(pub_id = resp['id'], titulo = resp['title'],desc = resp['descriptions'],precio=resp['price'],categoria = resp['listing_type_id'],activa = True, url = resp['permalink'],sincronizado = True).save()

            for id in set(pubs_django) - set(pubs_meli):
                item = Publicacion.objects.get(pub_id = id)
                item.sincronizado = False
                item.save()
            self.message_user(request,f'Publicaciones sincronizadas')
        else:
            self.message_user(request,f'Publicaciones no sincronizadas', level="ERROR")
              
    def creado(self,obj):
        return obj.f_creado.strftime("%d/%m/%y") 
        
    def actualizado(self,obj):
        try:
            return obj.f_actualizacion.strftime('%d/%m/%y')
        except:
            return ''
        
    def titulo_short(self,obj):
        return f"{obj.titulo.replace('Volkswagen','')[:15]}..." if len(obj.titulo.replace('Volkswagen','')) > 15 else obj.titulo.replace('Volkswagen','')
    titulo_short.short_description = 'titulo'

    def ver(self,obj):
        return format_html('<a href="{}" target=_blank>{}</a>', obj.url, 'Ir')
    
    def cat(self,obj):
        if obj.categoria == 'silver':
            return 'Plata'
        elif obj.categoria == 'gold':
            return 'Oro'
        else:
            return 'Oro Premium'

    @admin.action(description='Pausar / Activar')
    def pausar(self,request,objetos):
        api = MeliAPI(MeliCon.objects.get(name = 'API Dnogues'))
        for obj in objetos:
            if obj.activa == True:
                resp = api.pausar_eliminar_publicacion(obj.pub_id,'paused')
                if resp_ok(resp,'Pausar publicacion'):
                    obj.activa = False
                    obj.f_actualizacion = timezone.now()
                    obj.save()
                    self.message_user(request,f'{obj.pub_id} | Publicacion Pausada')
                else:
                    self.message_user(request,f'{obj.pub_id} | {resp.text}', level="ERROR")
            else:
                resp = api.pausar_eliminar_publicacion(obj.pub_id,'active')
                if resp_ok(resp,'Reactivar publicacion'):
                    obj.activa = True
                    obj.f_actualizacion = timezone.now()
                    obj.save()
                    self.message_user(request,f'{obj.pub_id} | Publicacion Activa')
                else:
                    self.message_user(request,f'{obj.pub_id} | {resp.text}', level="ERROR")

    @admin.action(description='Eliminar pub de Mercadolibre')
    def eliminar(self,request,objetos):
        api = MeliAPI(MeliCon.objects.get(name = 'API Dnogues'))
        for obj in objetos:
            resp1 = api.pausar_eliminar_publicacion(obj.pub_id,'closed')
            if resp1.status_code == 200:
                resp = api.pausar_eliminar_publicacion(obj.pub_id,'delete')
                if resp.status_code == 200:
                    self.message_user(request,f'{obj.pub_id} | Publicacion Eliminada correctamente')
                    obj.delete()
                else:
                    self.message_user(request,f'{obj.pub_id} | Publicacion Cerrada, pero no se pudo eliminar\nError: {resp.text}', level="ERROR")
            else:
                self.message_user(request,f'{obj.pub_id} | La publicacion no se pudo cerrar ni eliminar\nError: {resp1.text}', level="ERROR")

    @admin.action(description='Cambiar Precio')

    @admin.action(description='Sincronizar Publicaciones')
    def publicaciones_vendedor(self,request,objetos):
        api = MeliAPI(MeliCon.objects.get(name = 'API Dnogues'))
        resp = api.items_por_usuario_categoria(api.data.user_id)
    
    @admin.action(description='Actualizar Precio')
    def actualizar_precio(self,request,objetos):
        api = MeliAPI(MeliCon.objects.get(name = 'API Dnogues'))
        for obj in objetos:
            precio = convertir_precio(obj)
            if precio == 0:
                self.message_user(request,f'Precio invalido {precio}', level='ERROR')
                break
            resp = api.actualizar_precio(obj.pub_id,str(precio))
            if resp_ok(resp,'Camio Precio') == False:
                self.message_user(request,f'No se actualizo el precio {resp.text}', level='ERROR')
                break
            self.message_user(request,f'Publicacion {obj.pub_id} actualizada a {precio}')
                    
@admin.register(GrupoImagenes)
class GrupoImagenesAdmin(admin.ModelAdmin):
    list_display = ('codigo','nombre','cantidad','cargar_imagenes')

    def cargar_imagenes(self,obj):
        url = reverse('File_Uploads')
        return format_html('<a href="{}" target=_blank>{}</a>',url, 'Subir Imagenes')

    def cantidad(self,obj):
        return obj.imagenes.count()

@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ('unidad','anio','precio','precio_crm','categoria','publicaciones','cargar_imagenes','c_img','c_atrib')
    list_editable = ('precio','categoria')
    search_fields = ['descripcion']
    actions = ('publicar',)

    def precio_crm(self,obj):
        try:
            return obj.espasa_db.precio_tx if obj.espasa_db.ofertas == 0 else obj.espasa_db.oferta_min
        except:
            return 0
    
    def c_img(self,obj):
        try:
            return obj.g_imagenes.imagenes.count()
        except:
            return 0

    def c_atrib(self,obj):
        try:
            return obj.g_atributos.atributos.count()
        except:
            return 0

    def cargar_imagenes(self,obj):
        url = reverse('File_Uploads')
        return format_html("<a href='#' onclick=\"window.open('{}', 'Probando', 'width='+screen.width/2+',height='+screen.height/2); return false;\">{}</a>", url, 'Ir')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def unidad(self,obj):
        try:
            return f'{obj.espasa_db.codigo} | {obj.espasa_db.desc}'
        except:
            return ''
    
    def publicaciones(self,obj):
        return Publicacion.objects.filter(modelo = obj, activa = True).count()

    @admin.action(description='Publicar')
    def publicar(self,request,objetos):
        api = MeliAPI(MeliCon.objects.get(name = 'API Dnogues'))
        for obj in objetos:
            resp = api.publicar_auto(ArmarPublicacion(obj).pub())
            print(resp.status_code)
            if resp_ok(resp,'Publicar Auto'):
                resp = resp.json()
                pub = Publicacion.objects.create(pub_id = resp['id'], titulo = resp['title'],desc = obj.desc_meli,precio=resp['price'],categoria = resp['listing_type_id'],activa = True,modelo=obj, url = resp['permalink'], espasa_db=obj.espasa_db).save()
                desc = api.cambiar_desc(resp['id'] , obj.desc_meli)
                print(desc.status_code, desc.text)
                
                self.message_user(
                    request,
                    f"{obj.descripcion} | Publicado {resp['permalink']}"
                )
            else:
                self.message_user(request,f'{str(resp.text)}',level='ERROR')
    
@admin.register(Atributo)
class AtributoAdmin(admin.ModelAdmin):
    list_display = ('nombre','id_att','value')

@admin.register(GrupoAtributos)
class GrupoAtributosAdmin(admin.ModelAdmin):
    list_display = ('nombre','pub_to_copy','cantidad')
    list_editable = ('pub_to_copy',)
    actions = ('copiar_atributos',)
    
    def cantidad(self,obj):
        return obj.atributos.count()
    
    @admin.action(description='Copiar de Publicacion')
    def copiar_atributos(self,request,objetos):
        api = MeliAPI(MeliCon.objects.get(name = 'API Dnogues'))

        for obj in objetos:
            resp = api.consulta_pub(obj.pub_to_copy)
            if resp_ok(resp, 'Consultar Atributos'):
                for at in resp.json()['attributes']:
                    try:
                        apend = Atributo.objects.get(id_att=at['id'],value=at['value_name'])
                    except:
                        apend = Atributo.objects.create(nombre = at['name'] ,id_att=at['id'],value=at['value_name']).save()     
                    apend = Atributo.objects.get(id_att=at['id'],value=at['value_name'])
                    obj.atributos.add(apend)
            obj.save()

        self.message_user(
            request,
            f'{objetos.count()} | atributos copiados'
        )
    
@admin.register(MeliCon)
class MeliConAdmin(admin.ModelAdmin):
    list_display = ('name',)
    actions = ('get_credenciales',)
    
    @admin.action(description='Get Token')
    def get_credenciales(self,request,objetos):
        for obj in objetos:
            resp = MeliAPI(obj).auth_token()
            if resp_ok(resp, 'Autorizar Token'):
                obj.access_token = resp.json()['access_token']
                obj.refresh_secret = resp.json()['refresh_token']
                self.message_user(
                    request,
                    'Access token conseguido'
                )
            else:
                resp = MeliAPI(obj).renew_token()
                if resp_ok(resp, 'Renovar token'):
                    obj.access_token = resp.json()['access_token']
                    obj.refresh_secret = resp.json()['refresh_token']
                    self.message_user(request,f'Access Token renovado{resp.text}')
                else:
                    self.message_user(
                        request,
                        f'{str(resp.text)}', level="ERROR"
                    )
            obj.save()
            resp_user = MeliAPI(obj).get_user_me()
            if resp_ok(resp_user, 'Carga user ID'):
                obj.user_id = resp_user.json()['id']
                self.message_user(request,'User id cargado')
            else:
                self.message_user(request,f'User id no identificado {resp_user.text}')
            obj.save()