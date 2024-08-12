from django.contrib import admin
from .models import *
from .publicaciones import ArmarPublicacion, Descripciones
from .apicon import MeliAPI
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from usuarios.models import Cuenta
from django.forms.models import model_to_dict
import requests
from lead.models import Lead
from django.db.models import Sum

from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

admin.site.site_header = "Mercado Libre ESPASA DNogues"
admin.site.site_title = "Meli Espasa"

# api = MeliAPI(MeliCon.objects.get(name = 'API Dnogues'))

path = 'http://127.0.0.1:8000/'
#path = 'https://meli.dnoguesdev.com.ar/'

#Creo un filtro para los 0 Publicaciones
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Q

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

class PublicacionesCeroFilter(SimpleListFilter):
    title = 'publicaciones'
    parameter_name = 'publicaciones'

    def lookups(self, request, model_admin):
        return (
            ('0', 'Sin publicaciones'),
        )

    def queryset(self, request, queryset):
        # Filtrar objetos que tienen 0 publicaciones activas para la cuenta del usuario
        if self.value() == '0':
            return queryset.annotate(num_publicaciones=Count('publicacion', filter=Q(publicacion__cuenta__user=request.user))).filter(num_publicaciones=0)
        return queryset


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
class PubStatsAdmin(ModelAdmin):
    list_display = ('pub_id','views','clics_tel', 'ubicacion')
 


@admin.register(Errores)
class ErroresAdmin(ModelAdmin):
    list_display = ('name','fecha','error')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)

@admin.register(Publicacion)
class PublicacionAdmin(ModelAdmin):
    list_display=('titulo_short','pub_id','precio','crm','pub_vs_crm','stock','creado','vistas','cont','pub_ubicacion','cuenta','activa','ver','sincronizado','banner')
    list_editable =('precio',)
    list_filter = ['cuenta','activa']
    actions = ('pausar','eliminar','sinconizar_meli','actualizar_precios','revisar_activa','eliminar_v2','revisar_activa_v2','pagina')
    ordering = ['sincronizado','titulo']
    search_fields = ('titulo', 'pub_id','categoria','precio','activa')

    def pub_ubicacion (self,obj):
        try:
            return obj.stats.ubicacion
        except:
            return '-'

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
            return Lead.objects.filter(item_id=obj.pub_id).aggregate(total=Sum('contactos'))['total'] or 0
        except:
            return '-'                           
                           
    def creado(self,obj):
        return obj.f_creado.strftime("%d/%m/%y") 
        
    def titulo_short(self,obj):
        return f"{obj.titulo.replace('Volkswagen','')[:25]}..." if len(obj.titulo.replace('Volkswagen','')) > 25 else obj.titulo.replace('Volkswagen','')
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

    @admin.action(description='Eliminar pub ML V2')
    def eliminar_v2(self,request,objetos):
        cant_pubs = 0
        total_pubs = 0
        cuenta = Cuenta.objects.get(user = request.user)
        cuenta = model_to_dict(cuenta)
        payload = {'cuenta':cuenta}
        lista_pubs = []
        for obj in objetos:
            if obj.banner == True:
                self.message_user(request,f'Es un banner No se va a', level="ERROR")
                break
            total_pubs += 1
            lista_pubs.append(obj.pub_id)
        payload['lista_pubs'] = lista_pubs
        pub_res = requests.post(f"{path}/api/eliminar/", json=payload)
        for pub in pub_res.json()['pub_res']:
            try:
                if pub['sub_status'][0] == 'deleted':
                    objetos.filter(pub_id = pub['id']).delete()
                    cant_pubs += 1
                    self.message_user(request,f'{obj.pub_id} | Publicacion Eliminada correctamente')
            except:
                self.message_user(request,f"Error al eliminar", level="ERROR")
        self.message_user(request,f'Se eliminaron {cant_pubs} de {total_pubs} publicaciones')
            
        
        

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

    @admin.action(description="Revisar si esta ACTIVA")
    def revisar_activa(self,request,objetos):
        cuenta = Cuenta.objects.get(user = request.user)
        api = MeliAPI(cuenta)
        for obj in objetos:
            resp = api.consulta_pub(obj.pub_id)
            if resp_ok(resp, 'Consultando Estado de unidad'):
                if resp.json()['status'] == 'active':
                    obj.activa = True
                    obj.save()
                else:
                    obj.activa = False
                    obj.save()
                    self.message_user(request,f"{obj.pub_id} | {resp.json()['status']} | {resp.json()['sub_status']}", level="ERROR")
     
    @admin.action(description="Revisar si esta ACTIVA V2")
    def revisar_activa_v2(self,request,objetos):
        cant_pubs = 0
        total_pubs = 0
        cuenta = Cuenta.objects.get(user = request.user)
        cuenta = model_to_dict(cuenta)
        payload = {'cuenta':cuenta}
        lista_pubs = []
        for obj in objetos:
            total_pubs += 1
            lista_pubs.append(obj.pub_id)
        payload['lista_pubs'] = lista_pubs
        pub_res = requests.post(f"{path}/api/activa/", json=payload)
                
        for pub in pub_res.json()['pub_res']:
            if pub['status'] == 'active':
                objetos.filter(pub_id = pub['id']).update(activa = True)
                cant_pubs += 1
        self.message_user(request,f'{cant_pubs} de {total_pubs} publicaciones activas')
            
    @admin.action(description="Actualizar Precio")
    def actualizar_precios(self,request,objetos):
        for obj in objetos:
            try:
                precio =  obj.modelo.espasa_db.precio_tx if obj.modelo.espasa_db.ofertas == "0" else obj.modelo.espasa_db.oferta_min
            except:
                precio = 0
            obj.precio = convertir_precio2(precio)
            obj.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.username == 'dnogues':
            return qs
        qs = qs.filter(cuenta = Cuenta.objects.filter(user = request.user)[0])
        return qs
    
    @admin.action(description='Buscar Pagina')
    def pagina(self,request,objetos):
        from .meli_pos import PaginaPublicacion
        fecha = timezone.now().strftime("%d-%m")
        for obj in objetos:
            if obj.modelo.search_page != "":
                pagina, ubicacion = PaginaPublicacion(obj.modelo.search_page, obj.pub_id).search_page()
                
                if pagina == 0 and ubicacion == 0:
                    obj.stats.ubicacion = f"N/A|{fecha}"
                else:
                    obj.stats.ubicacion = f"{int(pagina)+1}|{int(ubicacion)+1}|{fecha}"
                obj.stats.save()
                self.message_user(request, f'{pagina, ubicacion}')
        
    
               
@admin.register(GrupoImagenes)
class GrupoImagenesAdmin(ModelAdmin):
    list_display = ('codigo','nombre','cantidad','cargar_imagenes')

    def cargar_imagenes(self,obj):
        url = reverse('File_Uploads') + f'?grupo_imagenes={obj.id}'
        return format_html('<a href="{}" target=_blank>{}</a>',url, 'Subir Imagenes')

    def cantidad(self,obj):
        return obj.imagenes.count()

@admin.register(Portadas)
class PortadasAdmin(ModelAdmin):
    list_display = ('codigo','nombre','cantidad','cargar_imagenes')

    def cargar_imagenes(self,obj):
        url = reverse('File_Uploads') + f'?portada_id={obj.id}'
        return format_html('<a href="{}" target=_blank>{}</a>',url, 'Subir Imagenes')

    def cantidad(self,obj):
        return obj.imagenes.count()

@admin.register(Modelo)
class ModeloAdmin(ModelAdmin):
    list_display = ('unidad','cantidad','precio','precio_crm','publicaciones','stock','cargar_portadas','cargar_imagenes','c_port','c_img','c_atrib','pub_to_copy')
    list_editable = ('precio','pub_to_copy','cantidad')
    search_fields = ['descripcion']
    actions = ('publicar','actualizar_precios','publicar_v2')
    list_filter = (PublicacionesCeroFilter,)
    
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
        cuenta = Cuenta.objects.get(user = request.user)
        return qs

    def unidad(self,obj):
        try:
            return f'{obj.espasa_db.codigo} | {obj.espasa_db.desc}'
        except:
            return ''
    
    def publicaciones(self,obj):
        return Publicacion.objects.filter(modelo = obj, cuenta = self.cuenta).count()
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
        cuenta = Cuenta.objects.get(user = request.user)
        api = MeliAPI(cuenta)
        bucles = sum(obj.cantidad for obj in objetos)
        if bucles > 6:
            self.message_user(request,'No se pueden hacer mas de 5 publicaciones a la vez',level='ERROR')
        else:
            for obj in objetos:
                for i in range(0,obj.cantidad):
                    resp = api.publicar_auto(ArmarPublicacion(obj).pub())
                    if resp_ok(resp,'Publicar Auto'):
                        resp = resp.json()
                        stats = PubStats.objects.create(pub_id = resp['id'])
                        stats.save()
                        pub = Publicacion.objects.create(pub_id = resp['id'], titulo = resp['title'],desc = obj.desc_meli,precio=resp['price'],categoria = resp['listing_type_id'],activa = False,modelo=obj, url = resp['permalink'], stats = stats, sincronizado = True, cuenta=cuenta).save()
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
                    obj.cantidad = 1
                    obj.save()

    #Version 2 para publicar de forma ASYNCRONA
    
    @admin.action(description='Publicar v2')
    def publicar_v2(self,request,objetos):
        cant_pubs = 0
        total_pubs = 0

        cuenta = Cuenta.objects.get(user = request.user)
        api = MeliAPI(cuenta)
        cuenta = model_to_dict(cuenta)
        payload = {'cuenta':cuenta}
        lista_pubs = []
        for obj in objetos:
            for i in range(0,obj.cantidad):
                lista_pubs.append(ArmarPublicacion(obj).pub())
                total_pubs += 1
            obj.cantidad = 1
            obj.save()
        payload['lista_pubs'] = lista_pubs

        pub_res = requests.post(f'{path}/api/publicar/',json=payload)
      
        try:
            cuenta = Cuenta.objects.get(id= pub_res.json()['cuenta']['id'])
            for resp in pub_res.json()['pub_res']:
                modelo = objetos.filter(descripcion__iexact = resp['title'].replace('Volkswagen ',''))
                cant_pubs += 1
                stats = PubStats.objects.create(pub_id = resp['id'])
                stats.save()
                try:
                    modelo = objetos.filter(descripcion__iexact = resp['title'].replace('Volkswagen ',''))
                    pub = Publicacion.objects.create(pub_id = resp['id'], titulo = resp['title'],desc = "",precio=resp['price'],categoria = resp['listing_type_id'],activa = False,modelo=modelo[0], url = resp['permalink'], stats = stats, sincronizado = True, cuenta=cuenta).save()
                except:
                    pub = Publicacion.objects.create(pub_id = resp['id'], titulo = resp['title'],desc = "",precio=resp['price'],categoria = resp['listing_type_id'],activa = False, url = resp['permalink'], stats = stats, sincronizado = True, cuenta=cuenta).save()
        except:
            pass
        
        self.message_user(request,f'Publicados {cant_pubs} de {total_pubs} publicaciones',level='SUCCESS')
        
        

    #Agrego self cuenta cuanto logueo
    def changelist_view(self, request, extra_context=None):
        self.request = request
        self.cuenta = Cuenta.objects.get(user = request.user)
        return super().changelist_view(request, extra_context=extra_context) 

  
@admin.register(Atributo)
class AtributoAdmin(ModelAdmin):
    list_display = ('nombre','id_att','value')

@admin.register(GrupoAtributos)
class GrupoAtributosAdmin(ModelAdmin):
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
class MeliConAdmin(ModelAdmin):
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