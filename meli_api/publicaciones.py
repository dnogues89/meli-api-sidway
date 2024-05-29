class ArmarPublicacion():
    def __init__(self, modelo) -> None:
      self.modelo = modelo
    
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
      for imagen in self.modelo.g_imagenes.imagenes.all()[::-1]:
        imagenes.append({
          'source':f"https://meli.dnoguesdev.com.ar{imagen.pic.url}"
        })
      return imagenes

    def pub(self):    
        json = {
        "title": f'Volkswagen {self.modelo.descripcion}',
        "description": "Okm publicacion de prueba",
        "channels": 
        [
        "marketplace" 
        ], 
        "pictures": self.imagenes(),
        "video_id": self.modelo.video_id,
        "category_id": "MLA1744",
        "price": str(self.modelo.precio),
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
          "country_code": "54",
          "area_code": "",
          "phone": "52787500",
          "country_code2": "54",
          "area_code2": "",
          "phone2": "1123149614",
          "email": "dnogues@espasa.com.ar",
          "webpage": ""
        },
        
        "attributes": self.atributes()
        }

        
        return json


class Descripciones():
  def __init__(self) -> None:
    self.get_descripcion()
    
  def get_descripcion(self):
    desc = """

Asesores Comerciales certificados por VW Argentina

- Hasta agotar stock en OFERTA
- Consecionario Oficial N°1 por 21 años consecutivos.
- El mejor precio del Mercado Asegurado!
- Acepto permuta por mayor o menor valor.
- Entrega inmediata.
- Disponibilidad de Colores.
- Financiación exclusiva.
- Estacionamiento gratuito.
- Consulte por esta y otras versiones o modelos.
- No incluye ningún gasto.
    
    """
    
    return desc