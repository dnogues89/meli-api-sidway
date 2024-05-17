from django.shortcuts import render
from .models import Lead
from meli_api.apicon import MeliAPI
from meli_api import models
from django.http import HttpResponse
from .salesforce_lead import Salesfroce

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
            except:
                pub = None
                
            try:
                item =Lead.objects.get(lead_id = lead['id'])
                if item.contactos != len(lead['leads']):
                    item.contactos = len(lead['leads'])
                    Salesfroce(item).send_data()
                    item.to_crm = True
                    item.save()
            except:
                item = Lead.objects.create(
                    lead_id = lead['id'],
                    item_id = pub,
                    name = lead['name'],
                    email = lead['email'],
                    phone = phone,
                    contactos = len(lead['leads'])
                )
                item.save()
                Salesfroce(item).send_data()
                item.to_crm = True
                item.save()
                
                
    return HttpResponse(f'{resp.json()}')