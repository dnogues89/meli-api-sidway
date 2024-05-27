from django.shortcuts import render
from .models import Lead
from meli_api.apicon import MeliAPI
from meli_api import models
from django.http import HttpResponse
from .salesforce_lead import Salesfroce

from django.utils import timezone
from datetime import timedelta


def generar_fechas(inicio, fin):
    # Convertimos las fechas a objetos datetime
    desde = timezone.datetime.strptime(inicio, "%Y-%m-%d")
    hasta = timezone.datetime.strptime(fin, "%Y-%m-%d")
    
    fechas = []
    
    while desde < hasta:
        # Si la fecha final es menor que "desde + 1 día", ajustamos "hasta" para la última iteración
        siguiente_hasta = min(desde + timedelta(days=1), hasta)
        # Convertimos las fechas a string y almacenamos en la lista
        fechas.append((desde.strftime("%Y-%m-%d"), siguiente_hasta.strftime("%Y-%m-%d")))
        
        # Incrementamos las fechas en 2 días
        desde += timedelta(days=2)
    
    return fechas

# Create your views here.
def get_leads(request):
    conn = models.MeliCon.objects.get(name = 'API Dnogues')
    api = MeliAPI(conn)
    resp = api.leads(conn.user_id)
    if models.resp_ok(resp,'Descargando Leads'):
        for lead in resp.json()['results']:
            try:
                phone = lead['phone']
            except:
                phone = '1111111111'
                
            try:
                pub = models.Publicacion.objects.get(pub_id = lead['item_id'])
                model = pub.modelo.descripcion
                familia = pub.modelo.espasa_db.familia
            except:
                pub = "-"
                model = '-'
                familia = '-'
                
            try:
                item =Lead.objects.get(lead_id = lead['id'])
                if item.contactos != len(lead['leads']):
                    item.origen = " | ".join([x['channel'] for x in lead['leads']])
                    item.contactos = len(lead['leads'])
                    item.save()
            except:
                item = Lead.objects.create(
                    lead_id = lead['id'],
                    item_id = lead['item_id'],
                    modelo = model,
                    familia = familia,
                    origen = " | ".join([x['channel'] for x in lead['leads']]),
                    date = lead['leads'][0]['created_at'],
                    name = lead['name'],
                    email = lead['email'],
                    phone = phone,
                    contactos = len(lead['leads'])
                )
                item.save()
            if 'whatsapp'not in item.origen:
                # Salesfroce(item).send_data()
                # item.to_crm = True
                item.save()
            
                
    return HttpResponse(f'{resp.json()}')

def get_leads_dia_dia(requests):
    conn = models.MeliCon.objects.get(name = 'API Dnogues')
    api = MeliAPI(conn)
    inicio = "2024-01-01"
    fin = timezone.now().strftime("%Y-%m-%d")

    fechas_generadas = generar_fechas(inicio, fin)
    
    for desde, hasta in fechas_generadas:
        resp = api.leads(conn.user_id, desde, hasta)
        if models.resp_ok(resp,'Descargando Leads'):
            if resp.json():
                for lead in resp.json()['results']:
                    try:
                        phone = lead['phone']
                    except:
                        phone = '1111111111'
                        
                    try:
                        pub = models.Publicacion.objects.get(pub_id = lead['item_id'])
                        model = pub.modelo.descripcion
                        familia = pub.modelo.espasa_db.familia
                    except:
                        pub = "-"
                        model = '-'
                        familia = '-'
                        
                    try:
                        item =Lead.objects.get(lead_id = lead['id'])
                        if item.contactos != len(lead['leads']):
                            item.origen = " | ".join([x['channel'] for x in lead['leads']])
                            item.contactos = len(lead['leads'])
                            item.save()
                    except:
                        item = Lead.objects.create(
                            lead_id = lead['id'],
                            item_id = lead['item_id'],
                            modelo = model,
                            familia = familia,
                            origen = " | ".join([x['channel'] for x in lead['leads']]),
                            date = lead['leads'][0]['created_at'],
                            name = lead['name'],
                            email = lead['email'],
                            phone = phone,
                            contactos = len(lead['leads'])
                        )
                        item.save() 