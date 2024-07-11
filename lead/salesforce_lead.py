import requests
import json
from django.core.mail import send_mail
# from .models import Key

def convertir_numero(numero):
    numero = numero.replace('-15-','').replace(' ','').replace('-','').replace(')15', '').replace('(','').replace(')','')
    numero = numero if numero[0] != '0' else numero [1:]
    return numero

class Salesfroce():
    def __init__(self, cliente, concesionario ="3046 - ESPASA S.A.", origen = "MLD") -> None:
        self.concesionario = concesionario
        self.origen = origen
        self.cliente = cliente
        self.get_data()
        

    def get_data(self):
        try:
            comentario = f"{self.cliente.cuit_info.marca} | {self.cliente.cuit_info.modelo} | {self.cliente.cuit_info.fecha_ultimo_pat.strftime('%m/%y')} | {self.cliente.modelo}"
        except:
            try:
                comentario = f"{self.cliente.modelo}"
            except:
                comentario = ""
        
        try:
            producto = f"{self.cliente.modelo}"
        except:
            producto = "Sin definir"
                
            
        self.apellido = self.cliente.name
        self.email = self.cliente.email
        self.telefono = self.cliente.phone
        self.comentario = comentario
        self.producto = producto
    
    def send_data(self):
        from_mail='pybotwhat@gmail.com'
        # asunto = 'prueba'
        asunto = 'Salesforce Web2Lead'
        mensaje = f"""
            Nombre: \n
            Apellido: {self.apellido}\n
            Email: {self.email}\n
            Teléfono: {str(self.telefono)}\n
            Origen: {self.origen}\n
            Concesionario: {self.concesionario}\n
            Campaña: Mercado Libre API\n
            Comentario: {self.comentario}\n
            País:\n
            Provincia:\n
            Localidad:\n
            Código Postal:\n
            Producto: {self.producto}\n
            """
        # send_mail(asunto,mensaje,from_mail,['dnogues@espasa.com.ar'])
        send_mail(asunto,mensaje,from_mail,['vw_emailtoleadservice@j-27sndpfxzeziihub3wz3ki0i9mngk47qm2qzpyudikkis5wmj3.f2-1j2mfeak.na173.apex.salesforce.com','dnogues@espasa.com.ar'])
    