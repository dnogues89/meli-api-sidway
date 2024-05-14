from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import models
import json
from meli_api.apicon import MeliAPI
from django.utils import timezone

# Create your views here.
def mis_pubs(request):
    return HttpResponse('Archivo no encontrado.')

def update_stats(request):
    pubs = models.Publicacion.objects.all()
    api = MeliAPI(models.MeliCon.objects.get(name = 'API Dnogues'))
    hasta = timezone.now().date().strftime('%Y-%m-%dT00:00:00.000')
    lista_pubs = [x.pub_id for x in pubs]
    resp = api.phone_by_items(','.join(lista_pubs),hasta)
    
    #Contactos telefonicos
    if models.resp_ok(resp, 'Obtener clicks en telefonos'):
        for item in resp.json():
            try:
                pub = pubs.get(pub_id = item['item_id'])
                pub.stats.clics_tel = item['total']
                pub.stats.save()
            except:
                pass
    
    #Vistas
    for item in pubs.exclude(stats__isnull=True):
        print(item.pub_id)
        desde = item.f_creado.strftime('%Y-%m-%dT00:00:00.000-00:00')
        resp = api.views_by_item(item.pub_id,desde,hasta)
        print(resp, resp.status_code)
        if models.resp_ok(resp, f'Get {item.pub_id} views'):
            print(resp.json()[0]['total_visits'])
            item.stats.views = int(resp.json()[0]['total_visits'])
            item.stats.save()
            
    
    return HttpResponse('Archivo no encontrado.')

def sincro_meli(request):
    api = MeliAPI(models.MeliCon.objects.get(name = 'API Dnogues'))
    resp = api.items_by_id(models.MeliCon.objects.get(name = 'API Dnogues').user_id)
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
                        modelo = models.Modelo.objects.get(pub_id__iexact = resp['id'])
                        models.Publicacion.objects.create(pub_id = resp['id'], titulo = resp['title'],desc = resp['descriptions'],precio=resp['price'],categoria = resp['listing_type_id'],activa = activa, url = resp['permalink'],sincronizado = True, modelo = modelo, stats=stats).save()
                    except:
                        stats = models.PubStats.objects.create(pub_id = resp['id'])
                        models.Publicacion.objects.create(pub_id = resp['id'], titulo = resp['title'],desc = resp['descriptions'],precio=resp['price'],categoria = resp['listing_type_id'],activa = activa, url = resp['permalink'],sincronizado = True, stats=stats).save()
    return HttpResponse('Archivo no encontrado.')