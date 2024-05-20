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
      for imagen in self.modelo.g_imagenes.imagenes.all():
        imagenes.append({
          'source':f"https://meli.dnoguesdev.com.ar{imagen.pic.url}"
        })
      return imagenes

    def pub(self):    
        json = {
        "title": self.modelo.descripcion,
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
            "address_line": "Triunvirato, 3661",
            "zip_code": "1427",
            "city": {
            "id": "TUxBQ0NBUGZlZG1sYQ"
            }
        },
        "seller_contact": {
          "contact": "",
          "other_info": "",
          "country_code": "",
          "area_code": "",
          "phone": "",
          "country_code2": "54",
          "area_code2": "",
          "phone2": "91123149614",
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
    CONSULTE POR TODOS LOS MODELOS ." EL MEJOR PRECIO DEL PAÍS STOCK PERMANENTE " PRECIOS REALES ....

""PAGAMOS MAS TU USADO""

--------------------------------------------------------------

(de menor, igual y hasta mayor valor)

Aceptamos 2 autos por compra de 0 Km

Financiamos la diferencia tasa 0%
--------------------------------------------------------------

ESPASA SA Concesionario Oficial VW

N1 en ventas, 20 años consecutivos !!

CASA CENTRAL, Triunvirato 3661 CABA


-------------------------------------------------------------

Abierto de Lunes a sabado de 9hs a 19hs !!


-------------------------------------------------------------

El mayor stock permanente del mercado;

Entrega inmediata, colores a elección !!!!

Superamos cualquier presupuesto escrito !
    
    """
    
    return desc