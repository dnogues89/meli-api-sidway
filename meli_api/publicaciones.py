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
          'source':f"https://meli.dnoguesdev.com.ar{portada_random.pic.url}"
        })
      for imagen in self.modelo.g_imagenes.imagenes.all()[1:24]:
        imagenes.append({
          'source':f"https://meli.dnoguesdev.com.ar{imagen.pic.url}"
        })
      imagenes.append({
          'source':f"http://meli.dnoguesdev.com.ar/media/MiniApp_Images/institucional.jpeg"
        })
      return imagenes

    def pub(self):    
        json = {
        "title": f'{self.publicacion_config.marca} {self.publicacion_config.descripcion}',
        "description": "Okm publicacion de prueba",
        "channels": 
        [
        "marketplace" 
        ], 
        "pictures": self.imagenes(),
        "video_id": self.modelo.video_id,
        "category_id": "MLA1744",
        "price": str(self.precio),
        "currency_id": "ARS",
        "listing_type_id": self.modelo.categoria,
        "available_quantity": "1",

        "location": {
              "address_line": "",
              "zip_code": "",
              "neighborhood": {
                "id": "TUxBQkJBTDMxMDZa",
                "name": "Balvanera"
              },
              "city": {
                "id": "TUxBQ0NBUGZlZG1sYQ",
                "name": "Capital Federal"
              },
              "state": {
                "id": "TUxBUENBUGw3M2E1",
                "name": "Capital Federal"
              },
              "country": {
                "id": "AR",
                "name": "Argentina"
              },
              "latitude": -34.6101223,
              "longitude": -58.4059406
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


class Descripciones():
  def __init__(self) -> None:
    self.get_descripcion()
    
  def get_descripcion(self):
    desc = self.publicacion_config.descripcion
    
    return desc + str('.'*random.randint(1,9))