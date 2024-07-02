from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from . import models
from .publicaciones import ArmarPublicacion, Descripciones

from meli_api.apicon import MeliAPI
from django.utils import timezone
from datetime import timedelta
from .admin import get_token
from .apicon import MeliApiAsync

import asyncio
import aiohttp
import json

from usuarios.models import Cuenta

from django.views.decorators.csrf import csrf_exempt


async def post(session, url,headers,payload):
    async with session.post(url=url,json=payload, headers= headers) as res:
        post_resp = await res.json()
        return post_resp

async def get(session, url,headers):
    async with session.get(url=url, headers= headers) as res:
        post_resp = await res.json()
        return post_resp

async def put(session, url,headers,payload):
    async with session.put(url=url,data=payload, headers= headers) as res:
        post_resp = await res.json()
        return post_resp

async def crear_publicaciones(session,url, headers,payload):
    async with session.post(url=url,json=payload, headers= headers) as res:
        pub_meli_resp = await res.json()
        return pub_meli_resp

async def cambiar_desc(session,url, headers,payload):
    async with session.put(url=url, data=payload, headers=headers) as res:
        desc_meli_resp = await res.json()
        return desc_meli_resp

# Create your views here.
def mis_pubs(request):
    return HttpResponse('Archivo no encontrado.')

def republicar(request):
    cuenta = Cuenta.objects.get(name='MeliTNV')
    # for cuenta in cuentas:
    api = MeliAPI(cuenta)
    pubs = models.Publicacion.objects.all().filter(cuenta = cuenta).exclude(banner = True)
    for pub in pubs:
        modelo = pub.modelo
        try:
            precio =  modelo.espasa_db.precio_tx if modelo.espasa_db.ofertas == "0" else modelo.espasa_db.oferta_min
        except:
            precio = 0
        modelo.precio = models.convertir_precio2(precio)
        modelo.save()
        
        resp = api.pausar_eliminar_publicacion(pub.pub_id,'closed')
        if resp.status_code == 200:
            api.pausar_eliminar_publicacion(pub.pub_id,'delete')
            if resp.status_code == 200:
                pub = models.Publicacion.objects.get(pub_id = pub.pub_id)
                pub.delete()
                resp = api.publicar_auto(ArmarPublicacion(modelo).pub())
                if models.resp_ok(resp,'Publicar Auto'):
                    resp = resp.json()
                    stats = models.PubStats.objects.create(pub_id = resp['id'])
                    stats.save()
                    pub = models.Publicacion.objects.create(pub_id = resp['id'], titulo = resp['title'],desc = modelo.desc_meli,precio=resp['price'],categoria = resp['listing_type_id'],activa = False,modelo=modelo, url = resp['permalink'], stats = stats, sincronizado = True, cuenta=cuenta).save()
                    desc = api.cambiar_desc(resp['id'] , Descripciones().get_descripcion())
    return HttpResponse('Proceso terminado')                         
                               

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
        api = MeliAPI(cuenta)
        resp = api.preguntas(cuenta.user_meli)
        if models.resp_ok(resp, 'Levantando preguntas'):
            for preg in resp.json()['questions']:
                if preg['status'] == "UNANSWERED":
                    resp_q = api.responder_pregunta(preg['id'],'GRACIAS POR CONTACTARNOS EN ESPASA S.A. \nPor favor escribinos por whatsapp a 11-2314-9614 para que te podamos dar la mejor atencion, o haciendo click en el icono de whatsapp de la publicacion.\nTe vamos a contactar en menos de 30 minutos.')
                    if models.resp_ok(resp_q,f"Respondiendo pregunta{preg['id']}"):
                        pass
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
                        stats = models.PubStats.objects.filter(pub_id = resp['id'])[0]
                        item.f_creado = resp['date_created']
                        item.stats = stats
                        item.save()
    return HttpResponse('Archivo no encontrado.')

def publicacion(request,publicacion):
    try:
        return HttpResponse(models.Publicacion.objects.get(pub_id = publicacion).cuenta.salesforce_group)
    except:
        return HttpResponse('WAT')


@csrf_exempt
async def publicar_v2(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cuenta = data['cuenta']
        api = MeliApiAsync(cuenta['user_meli'],cuenta['access_token'])
        actions = []
        pub_res = []
        async with aiohttp.ClientSession() as session:
            for pub in data['lista_pubs']:
                url, headers,payload = api.publicar_auto(pub)
                actions.append(asyncio.ensure_future(post(session, url,headers,payload)))
            
            meli_pubs_res = await asyncio.gather(*actions)
            cambiar_desc_actions = []
            
            for pub in meli_pubs_res:
                url,headers,payload =  api.cambiar_desc(pub['id'])
                cambiar_desc_actions.append(asyncio.ensure_future(put(session, url,headers,payload)))
            
            _ = await asyncio.gather(*cambiar_desc_actions)
                        
            for data in meli_pubs_res:
                pub_res.append(data)
            
            data = {'pub_res':pub_res,'cuenta':cuenta}
    
    return JsonResponse(data,safe=False)

@csrf_exempt   
async def eliminar_pubs(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cuenta = data['cuenta']
        api = MeliApiAsync(cuenta['user_meli'],cuenta['access_token'])
        actions = []
        pub_res = []
        async with aiohttp.ClientSession() as session:
            for pub in data['lista_pubs']:
                url,headers,payload = api.pausar_eliminar_publicacion(pub,'closed')
                actions.append(asyncio.ensure_future(put(session, url,headers,payload)))
            
            pub_paused = await asyncio.gather(*actions)
            
            for pub in data['lista_pubs']:
                url,headers,payload = api.pausar_eliminar_publicacion(pub,'delete')
                actions.append(asyncio.ensure_future(put(session, url,headers,payload)))
            
            meli_pubs_res = await asyncio.gather(*actions)
            
            for data in meli_pubs_res:
                pub_res.append(data)
            
            data = {'pub_res':pub_res,'cuenta':cuenta}
    
    return JsonResponse(data,safe=False)

@csrf_exempt
async def activa(request):
    print('entre')
    if request.method == 'POST':
        data = json.loads(request.body)
        cuenta = data['cuenta']
        api = MeliApiAsync(cuenta['user_meli'],cuenta['access_token'])
        actions = []
        pub_res = []
        async with aiohttp.ClientSession() as session:
            for pub in data['lista_pubs']:
                url,headers,payload = api.consulta_pub(pub)
                actions.append(asyncio.ensure_future(get(session, url,headers)))
            
            resp = await asyncio.gather(*actions)
            
            for data in resp:
                pub_res.append(data)
                
            data = {'pub_res':pub_res,'cuenta':cuenta}
    
    return JsonResponse(data,safe=False)