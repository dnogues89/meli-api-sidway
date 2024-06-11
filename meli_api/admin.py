from django.contrib import admin
from .models import *
from .publicaciones import ArmarPublicacion, Descripciones
from .apicon import MeliAPI
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse

from usuarios.models import Cuenta


admin.site.site_header = "Mercado Libre ESPASA DNogues"
admin.site.site_title = "Meli Espasa"

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

def get_token(obj:Cuenta):
        api = MeliAPI(obj)
        try:
            if api.get_user_me().json()['message'] == 'invalid_token':
                resp = MeliAPI(obj).renew_token()
                if resp_ok(resp, 'Renovar token'):
                    obj.access_token = resp.json()['access_token']
                    obj.refresh_secret = resp.json()['refresh_token']
                else:
                    return False
                obj.save()
                return 'renovado'
        except:
            return False

    
# Register your models here.
@admin.register(PubStats)
class PubStatsAdmin(admin.ModelAdmin):
    list_display = ('pub_id','views','clics_tel')


@admin.register(Errores)
class ErroresAdmin(admin.ModelAdmin):
    list_display = ('name','fecha','error')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)

@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display=('titulo_short','pub_id', 'cat','precio','crm','pub_vs_crm','stock','creado','vistas','cont','cuenta','activa','ver','sincronizado','banner')
    list_editable =('precio',)
    actions = ('pausar','eliminar','sinconizar_meli')
    ordering = ['sincronizado','titulo']
    search_fields = ('titulo', 'pub_id','categoria','precio','activa')

    def pub_vs_crm(self,obj):
        try:
            crm = obj.modelo.espasa_db.precio_tx if obj.modelo.espasa_db.ofertas == '0' else obj.modelo.espasa_db.oferta_min
            crm = int(crm.replace("$","").replace(".",""))
            pub = int(obj.precio.replace("$","").replace(".",""))
            return "$ {:,.0f}".format(pub - crm).replace(",", ".")
        except:
            return 'Error'
            
    def crm(self,obj):
        try:
            return obj.modelo.espasa_db.precio_tx if obj.modelo.espasa_db.ofertas == '0' else obj.modelo.espasa_db.oferta_min
        except:
            return 0
    
    def stock(self,obj):
        try:
            return obj.modelo.espasa_db.stock
        except:
            return '-'
    
    def vistas(self,obj):
        try:
            return obj.stats.views
        except:
            return '-'
     
    def cont(self,obj):
        try:
            return obj.stats.clics_tel
        except:
            return '-'
       
    @admin.action(description='Sincronizar pubs con Meli')
    def sinconizar_meli(self,request,objetos):
        
        for obj in objetos:
            api = MeliAPI(obj.cuenta)
            resp = api.consulta_pub(obj)
            if resp_ok(resp, f'Consultando publicacion | {obj.pub_id}'):
                resp = resp.json()
                #Precio
                if resp['price'] != convertir_precio(obj):
                    precio = convertir_precio(obj)
                    if precio == 0:
                        self.message_user(request,f'Precio invalido {precio}', level='ERROR')
                        break
                    resp = api.actualizar_precio(obj.pub_id,str(precio))
                    if resp_ok(resp,'Cambio Precio') == False:
                        self.message_user(request,f'No se actualizo el precio {resp.text}', level='ERROR')
                        break
                    self.message_user(request,f'Publicacion {obj.pub_id} actualizada a {precio}')
                    obj.sincronizado = True
                    obj.save()
                            
                           
    def creado(self,obj):
        return obj.f_creado.strftime("%d/%m/%y") 
        
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
        for obj in objetos:
            api = MeliAPI(obj.cuenta)
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
        for obj in objetos:
            api = MeliAPI(obj.cuenta)
            if obj.banner == True:
                self.message_user(request,f'Es un banner No se va a', level="ERROR")
                break
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
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.username == 'dnogues':
            return qs
        qs = qs.filter(cuenta = Cuenta.objects.filter(user = request.user)[0])
        return qs
    
               
@admin.register(GrupoImagenes)
class GrupoImagenesAdmin(admin.ModelAdmin):
    list_display = ('codigo','nombre','cantidad','cargar_imagenes')

    def cargar_imagenes(self,obj):
        url = reverse('File_Uploads') + f'?grupo_imagenes={obj.id}'
        return format_html('<a href="{}" target=_blank>{}</a>',url, 'Subir Imagenes')

    def cantidad(self,obj):
        return obj.imagenes.count()

@admin.register(Portadas)
class PortadasAdmin(admin.ModelAdmin):
    list_display = ('codigo','nombre','cantidad','cargar_imagenes')

    def cargar_imagenes(self,obj):
        url = reverse('File_Uploads') + f'?portada_id={obj.id}'
        return format_html('<a href="{}" target=_blank>{}</a>',url, 'Subir Imagenes')

    def cantidad(self,obj):
        return obj.imagenes.count()

@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ('unidad','precio','precio_crm','categoria','cuenta','publicaciones','stock','cargar_portadas','cargar_imagenes','c_port','c_img','c_atrib','pub_to_copy')
    list_editable = ('precio','categoria','cuenta','pub_to_copy')
    search_fields = ['descripcion']
    actions = ('publicar','actualizar_precios')
    
    def stock(self,obj):
        try:
            return obj.espasa_db.stock
        except:
            return '-'

    def precio_crm(self,obj):
        try:
            return obj.espasa_db.precio_tx if obj.espasa_db.ofertas == "0" else obj.espasa_db.oferta_min
        except:
            return 0
    
    def c_img(self,obj):
        try:
            return obj.g_imagenes.imagenes.count()
        except:
            return 0

    def c_port(self,obj):
        try:
            return obj.portadas.imagenes.count()
        except:
            return 0

    def c_atrib(self,obj):
        try:
            return obj.g_atributos.atributos.count()
        except:
            return 0

    def cargar_imagenes(self,obj):
        url = reverse('File_Uploads') + f'?grupo_imagenes={obj.id}'
        return format_html('<a href="{}" >{}</a>', url, 'Imagenes')
    cargar_imagenes.short_description = 'Up/img'

    def cargar_portadas(self,obj):
        url = reverse('File_Uploads') + f'?portada_id={obj.id}'
        return format_html('<a href="{}" >{}</a>', url, 'Portadas')
    cargar_portadas.short_description = 'Up/portadas'

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
    publicaciones.short_description = 'pubs'

    @admin.action(description="Actualizar Precio")
    def actualizar_precios(self,request,objetos):
        for obj in objetos:
            try:
                precio =  obj.espasa_db.precio_tx if obj.espasa_db.ofertas == "0" else obj.espasa_db.oferta_min
            except:
                precio = 0
            obj.precio = convertir_precio2(precio)
            obj.save()

    @admin.action(description='Publicar')
    def publicar(self,request,objetos):
        for obj in objetos:
            api = MeliAPI(obj.cuenta)
            resp = api.publicar_auto(ArmarPublicacion(obj).pub())
            print(resp.status_code)
            if resp_ok(resp,'Publicar Auto'):
                resp = resp.json()
                stats = PubStats.objects.create(pub_id = resp['id'])
                stats.save()
                pub = Publicacion.objects.create(pub_id = resp['id'], titulo = resp['title'],desc = obj.desc_meli,precio=resp['price'],categoria = resp['listing_type_id'],activa = True,modelo=obj, url = resp['permalink'], stats = stats, sincronizado = True, cuenta=obj.cuenta).save()
                desc = api.cambiar_desc(resp['id'] , Descripciones().get_descripcion())
                if resp_ok(desc,f"Cambiando desc | {resp['id']}"):
                    self.message_user(
                        request,
                        f"{Descripciones().get_descripcion()} | Publicado {resp['permalink']}"
                    )
                else:
                    self.message_user(request,f'{str(resp.text)}',level='ERROR')
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
                obj.video_id = resp.json()['video_id'] 
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