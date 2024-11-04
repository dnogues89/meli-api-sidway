from django.shortcuts import render
from .models import Lead
from meli_api.apicon import MeliAPI
from meli_api import models
from .models import Lead, Usado, Cuit
from django.http import HttpResponse
from .salesforce_lead import Salesfroce, convertir_numero

from datetime import datetime

from .siomaa_api import Sioma_API

from usuarios.models import Cuenta

from django.utils import timezone
from datetime import timedelta

from espasa_info.espasa_conn import EspasaDataBase

# def cuit_info(request,telefono):
#     try:
#         lead = Lead.objects.filter(phone=telefono)[0]
#         cuit_info = f"Usado: {lead.cuit_info.marca} {lead.cuit_info.modelo} | Pat: {lead.cuit_info.fecha_ultimo_pat.strftime('%m/%y')} | Cliente: {lead.cuit_info.cliente}"
#         return HttpResponse(cuit_info)
#     except:
#         return HttpResponse('None')
def cuit_info(request,telefono):
    try:
        lead = Lead.objects.filter(phone=telefono)[0]
        usados = lead.siomaa_info.usados.filter(venta = None)
        posesion = "Posesion: "
        if usados.count() <= 3:
            for i in usados:
                posesion = f"{posesion} {i.marca} {i.modelo} {i.version} {i.anio} | "
        cuit_info = f"Cant: {lead.siomaa_info.usados.count()} | 0Km comprados: {lead.siomaa_info.usados.filter(cerokm=True).count()} | Prendas: {lead.siomaa_info.usados.filter(tipo_compra='Prenda').count()} | {posesion}"
        return HttpResponse(cuit_info)
    except:
        return HttpResponse('None')

def limpiar_lead(lead):
    try:
        phone = "".join(lead['phone'].split(' ')[1:])
    except:
        phone = '1111111111'
        
    try:
        name = lead['name']
    except:
        name = 'Estimado'
    
    try:
        email = lead['email']
    except:
        email = 'sin@mail.com'
        
    try:
        cuit = lead['identification_number']
    except:
        cuit = '00000000000'
        
    return phone , name, email, cuit

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
    cuentas = Cuenta.objects.all()
    for cuenta in cuentas:
        api = MeliAPI(cuenta)
        desde = Lead.objects.latest('date').date.strftime("%Y-%m-%d")
        resp = api.leads(cuenta.user_meli,desde)
        if models.resp_ok(resp,f'Descargando Leads {cuenta}'):
            leads = resp.json()['results']
            if leads == None:
                break
            for lead in leads:
                phone , name, email, cuit = limpiar_lead(lead)
                
                if phone == '1111111111' and email == 'sin@mail.com':
                    break
                
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
                    created_at = datetime.fromisoformat(lead['leads'][0]['created_at'].replace("Z", "+00:00"))
                    item_date = item.date if item.date.tzinfo else item.date.replace(tzinfo=timezone.utc)
                    
                    if item.contactos != len(lead['leads']):
                        item.origen = " | ".join([x['channel'] for x in lead['leads']])
                        item.contactos = len(lead['leads'])
                        item.phone = phone
                        if item_date != created_at:
                            item.date = created_at
                            item.to_crm = False
                        if lead['leads'][0]['channel'] == 'whatsapp':
                            item.to_crm =True
                        if lead['leads'][0]['channel'] == 'view':
                            item.to_crm =True
                        item.save()
                except:
                    
                    item = Lead.objects.create(
                        lead_id = lead['id'],
                        item_id = lead['item_id'],
                        modelo = model,
                        familia = familia,
                        origen = " | ".join([x['channel'] for x in lead['leads']]),
                        date = lead['leads'][0]['created_at'],
                        name = name,
                        email = email,
                        phone = phone,
                        cuit = cuit,
                        contactos = len(lead['leads']),
                        cuenta = cuenta
                    )
                    item.save()
                    if lead['leads'][0]['channel'] == 'whatsapp':
                        item.to_crm =True
                    if lead['leads'][0]['channel'] == 'view':
                        item.to_crm =True
                    item.save()
                    
                if item.to_crm == False:
                    Salesfroce(item, origen=cuenta.salesforce_group).send_data()
                    item.to_crm = True
                    item.save()
                
                #NUEVO
                if item.cuit:
                    try:
                        obj = Cuit.objects.get(cuil = item.cuit)
                    except:
                        obj = Cuit.objects.create(cuil = item.cuit)
                        obj.save()
                        
                    obj = Cuit.objects.get(cuil = item.cuit)   
                    siomaa = Sioma_API(obj.cuil).get_data()
                    if siomaa:
                        if obj.nombre == None:
                            obj.nombre = siomaa['Nombre']
                            obj.localidad = siomaa['Localidad']
                            obj.dni = siomaa['DNIConsultado']
                            obj.save()
                        for i in siomaa['HistoricoCompras']:
                            try:
                                usado = Usado.objects.get(id_sioma = i['IdOperacion']) 
                            except:
                                usado = Usado.objects.create(
                                    id_sioma = i['IdOperacion'],
                                    compra=datetime.strptime(i['FechaOperacion'], '%Y-%m-%dT%H:%M:%S').date() if i['FechaOperacion'] else None,
                                    marca=i['Marca'],
                                    modelo=i['Modelo'],
                                    version=i['Version'],
                                    anio=i['AnioModelo'],
                                    cerokm=True if i['C0KM'] == 'Si' else False,
                                    venta=datetime.strptime(i['FechaVenta'], '%Y-%m-%dT%H:%M:%S').date() if i['FechaVenta'] else None,
                                    tipo_compra='Prenda' if i['TipoCompra'] == 'Prenda' else 'Cash',
                                    tipo_acreedor=i['TipoAcreedor'],
                                    acreedor=i['Acreedor']
                                ).save()
                            usado = Usado.objects.get(id_sioma = i['IdOperacion']) 
                            obj.usados.add(usado)
                            item.siomaa_info = obj
                            item.save()
                                
            
                
    return HttpResponse(f'{resp.json()}')

# def get_leads_dia_dia(requests):
    conn = models.MeliCon.objects.get(name = 'API Dnogues')
    api = MeliAPI(conn)
    inicio = "2024-01-01"
    fin = timezone.now().strftime("%Y-%m-%d")

    fechas_generadas = generar_fechas(inicio, fin)
    
    for desde, hasta in fechas_generadas:
        resp = api.leads(conn.user_id, desde, hasta)
        if models.resp_ok(resp,'Descargando Leads'):
            if resp.json()['results'] != None:
                for lead in resp.json()['results']:
                    try:
                        phone = lead['phone']
                        phone = convertir_numero(lead['phone'])
                    except:
                        phone = '1111111111'
                        
                    try:
                        name = lead['name']
                    except:
                        name = 'Estimado'
     
                    try:
                        mail = lead['email']
                    except:
                        mail = 'sin@mail.com'
                    
                    if phone == '1111111111' and mail == 'sin@mail.com':
                        break
                        
                    
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
                            name = name,
                            email = mail,
                            phone = phone,
                            contactos = len(lead['leads'])
                        )
                        item.save()
                        
    return HttpResponse(f'Done')