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
        "video_id": self.modelo.g_imagenes.video,
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
        
        
        "attributes": self.atributes()
        }
        
        return json
    