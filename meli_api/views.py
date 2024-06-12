from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import models

from meli_api.apicon import MeliAPI
from django.utils import timezone
from datetime import timedelta
from .admin import get_token

from usuarios.models import Cuenta

# Create your views here.
def mis_pubs(request):
    return HttpResponse('Archivo no encontrado.')

def update_stats(request):
    cuentas = Cuenta.objects.all()
    for cuenta in cuentas:
        api = MeliAPI(cuenta)
        get_token(cuenta)
        pubs = models.Publicacion.objects.filter(cuenta = cuenta)
        hasta = timezone.now().date().strftime('%Y-%m-%dT00:00:00.000')
        lista_pubs = [x.pub_id for x in pubs]
        
        # Dividir la lista de publicaciones en sublistas de 5 elementos
        sublistas_pubs = [lista_pubs[i:i+5] for i in range(0, len(lista_pubs), 5)]
        
        
        for sublist in sublistas_pubs:
            resp = api.phone_by_items(','.join(sublist), hasta)
            
            # Contactos telefónicos
            if models.resp_ok(resp, 'Obtener clicks en telefonos'):
                for item in resp.json():
                    try:
                        pub = pubs.get(pub_id=item['item_id'])
                        pub.stats.clics_tel = item['total']
                        pub.stats.save()
                    except:
                        pass
        
        #Vistas
        for item in pubs.exclude(stats__isnull=True):
            desde = (item.f_creado - timedelta(days=1)).strftime('%Y-%m-%dT00:00:00.000-00:00')
            resp = api.views_by_item(item.pub_id,desde,hasta)
            print(resp.text)
            print(item.pub_id,desde,hasta)
            if models.resp_ok(resp, f'Get {item.pub_id} views'):
                print(resp.json()[0]['total_visits'])
                item.stats.views = int(resp.json()[0]['total_visits'])
                item.stats.save()
            
    
    return HttpResponse('Archivo no encontrado.')

def preguntas(request):
    cuentas = Cuenta.objects.all()
    for cuenta in cuentas:
        get_token(cuenta)
        api = MeliAPI(cuenta)
        resp = api.preguntas(cuenta.user_meli)
        if models.resp_ok(resp, 'Levantando preguntas'):
            for preg in resp.json()['questions']:
                if preg['status'] == "UNANSWERED":
                    resp_q = api.responder_pregunta(preg['id'],'GRACIAS POR CONTACTARNOS EN ESPASA S.A. \nPor favor escribinos por whatsapp a 11-2314-9614 para que te podamos dar la mejor atencion, o haciendo click en el icono de whatsapp de la publicacion.\nTe vamos a contactar en menos de 30 minutos.')
                    if models.resp_ok(resp_q,f"Respondiendo pregunta{preg['id']}"):
                        pass
            return HttpResponse(f'{resp.json()}')
        
    
    return HttpResponse(f'{resp.json()}')

def sincro_meli(request):
    cuentas = Cuenta.objects.all()
    for cuenta in cuentas:
        api = MeliAPI(cuenta)
        resp = api.items_by_id(cuenta.user_meli)
        if models.resp_ok(resp,'Buscando Publicaciones'):
                pubs_meli = resp.json()['results']
                pubs_django = [obj.pub_id for obj in  models.Publicacion.objects.all()]
                for obj in set(pubs_meli) - set(pubs_django):
                    resp = api.consulta_pub(obj)
                    if models.resp_ok(resp,'Consulta publicacion'):
                        resp = resp.json()
                        activa = True if resp['status'] == 'active' else False
                        try:
                            stats = models.PubStats.objects.create(pub_id = resp['id']).save()
                            modelo = models.Modelo.objects.get(descripcion__iexact = resp['title'])
                            models.Publicacion.objects.create(pub_id = resp['id'], titulo = resp['title'],desc = resp['descriptions'],precio=resp['price'],categoria = resp['listing_type_id'],activa = activa, url = resp['permalink'],sincronizado = True, modelo = modelo, stats=stats, cuenta=cuenta).save()

                        except:
                            models.Publicacion.objects.create(pub_id = resp['id'], titulo = resp['title'][11:],desc = resp['descriptions'],precio=resp['price'],categoria = resp['listing_type_id'],activa = activa, url = resp['permalink'],sincronizado = True, cuenta=cuenta).save()

                        item = models.Publicacion.objects.get(pub_id = resp['id'])
                        stats = models.PubStats.objects.get(pub_id = resp['id'])
                        item.f_creado = resp['date_created']
                        item.stats = stats
                        item.save()
    return HttpResponse('Archivo no encontrado.')

def publicacion(request,publicacion):
    try:
        return HttpResponse(models.Publicacion.objects.get(pub_id = publicacion).cuenta.salesforce_group)
    except:
        return HttpResponse('WAT')
    