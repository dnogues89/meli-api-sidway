from django.shortcuts import render, redirect
from .models import CRM
from .espasa_conn import EspasaDataBase
from meli_api.models import Modelo


# Create your views here.
def update_espasa_db(request):
    desc_meli = """
    """
    conn = EspasaDataBase()
    for item in conn.get_info():
        try:
            obj = CRM.objects.get(codigo = item[0])
            obj.desc = str(item[1])
            obj.familia = str(item[2])
            obj.precio_lista = str(item[3])
            obj.impuestos_internos = str(item[4])
            obj.precio_tx = str(item[5])
            obj.stock = str(item[6])
            obj.ofertas = str(item[7])
            obj.oferta_min = str(item[8]).split('.')[0] if item[8] is not None else 0
            obj.oferta_max = str(item[9]).split('.')[0] if item[9] is not None else 0
            obj.save()
            print(f'item actualizado {obj}')
            if str(item[6]) != '0':
                try:
                    _ = Modelo.objects.get(espasa_db__codigo = item[0])
                except:
                    _ = Modelo.objects.create(espasa_db = obj, descripcion = str(item[1]), anio = f"20{str(item[1]).split('MY')[-1].split(' ')[0]}", desc_meli=desc_meli).save()
            
        except:
                
            obj = CRM.objects.create(
                codigo = item[0],
                desc = item[1],
                familia = item[2],
                precio_lista = item[3],
                impuestos_internos = item[4],
                precio_tx = item[5],
                stock = item[6],
                ofertas = item[7],
                oferta_min = str(item[8]).split('.')[0] if item[8] is not None else 0,
                oferta_max = str(item[9]).split('.')[0] if item[8] is not None else 0
            ).save()
            print(f'item Creado {obj}')
            if str(item[6]) != '0':
                try:
                    _ = Modelo.objects.get(espasa_db__codigo = item[0])
                except:
                    _ = Modelo.objects.create(espasa_db = obj, descripcion = str(item[1]), anio = f"20{str(item[1]).split('MY')[-1].split(' ')[0]}",desc_meli=desc_meli).save()
        
        to_delete = Modelo.objects.filter(espasa_db__isnull=True)
        for item in to_delete:
           item.delete()
        
    return render(request, 'confirmacion.html')