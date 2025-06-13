import random

class ArmarPublicacion():
    def __init__(self, modelo, cuenta) -> None:
      self.modelo = modelo
      self.publicacion_config = cuenta.publicacion_config
      self.precio = str(self.modelo.precio)[:-1] + str(random.randint(1,9))
    
    def atributes(self):
      atributos = []
      for att in self.modelo.g_atributos.atributos.all():
        atributos.append({
          "id":att.id_att,
          "value_name":att.value
        })
      
      return atributos
      
    def imagenes(self):
      imagenes = []
      portada_random = random.choice(self.modelo.portadas.imagenes.all())
      imagenes.append({
          'source':f"https://melisidway.dnoguesdev.com.ar{portada_random.pic.url}"
        })
      for imagen in self.modelo.g_imagenes.imagenes.all()[1:24]:
        imagenes.append({
          'source':f"https://melisidway.dnoguesdev.com.ar{imagen.pic.url}"
        })
      imagenes.append({
          'source':f"http://melisidway.dnoguesdev.com.ar/media/MiniApp_Images/institucional.jpeg"
        })
      return imagenes

    def pub(self):    
        json = {
        "title": f'{self.modelo.marca} {self.modelo.descripcion}',
        "description": "Okm publicacion de prueba",
        "channels": 
        [
        "marketplace" 
        ], 
        "pictures": self.imagenes(),
        "video_id": self.modelo.video_id,
        "category_id": "MLA1744",
        "price": str(self.precio),
        "currency_id": "ARS" if self.modelo.espasa_db.moneda == "1" else "USD",
        "listing_type_id": self.modelo.categoria,
        "available_quantity": "1",

        "location": {
            "address_line": "De Los Incas 4831",
            "zip_code": "1427",
            # "neighborhood": {
            #     "id": "TVhYUGFycXVlIENoYXNUVXhCUTBOQlVHWmxaR",
            #     "name": "Parque Chas"
            # },
            "city": {
                "id": "QVItQ1BhcnF1ZSBDaGFz",
                "name": "Parque Chas"
            },
            "state": {
                "id": "AR-C",
                "name": "Capital Federal"
            },
            "country": {
                "id": "AR",
                "name": "Argentina"
            }
        },
        "seller_contact": {
          "contact": "",
          "other_info": "",
          "country_code": "",
          "area_code": "011",
          "phone": f"{self.publicacion_config.telefono_sucursal}",
          "country_code2": "54",
          "area_code2": "",
          "phone2": f"{self.publicacion_config.whatsapp}",
          "email": f"{self.publicacion_config.email_sucursal}",
          "webpage": ""
        },
        
        "attributes": self.atributes()
        }

        
        return json
