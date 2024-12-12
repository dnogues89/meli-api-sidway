import requests
import json

class LeadTecnom():
    def __init__(self, cliente) -> None:
        self.cliente = cliente
        self.get_data()
        self.send_lead()

    def get_data(self):
        try:
            usados = self.cliente.siomaa_info.usados.filter(venta = None)
            posesion = f"Posesion: {usados.count()}"
            for i in usados[0:3]:
                posesion = f"{posesion} {i.marca} {i.modelo} {i.version} {i.anio} | "
            comentario = f"Op Totales: {self.cliente.siomaa_info.usados.count()} | 0Km: {self.cliente.siomaa_info.usados.filter(cerokm=True).count()} | Prendas: {self.cliente.siomaa_info.usados.filter(tipo_compra='Prenda').count()} | {posesion}"
        except:
            try:
                comentario = f"{self.cliente.modelo}"
            except:
                comentario = ""
        
        try:
            producto = f"{self.cliente.modelo}"
        except:
            producto = "Sin definir"
                
            
        self.name = self.cliente.name
        self.email = self.cliente.email
        self.telefono = self.cliente.phone
        self.comentario = comentario
        self.producto = producto

    def send_lead(self):
        json_data = json.dumps(self.build_lead())
        url = "https://sidway.tecnomcrm.com/api/v1/webconnector/consultas/adf"
        headers = {
            "Content-Type" : "application/json ",
            }
        username = "dnogues@espasa.com.ar"
        password = "123456"
        headers = {"Content-Type" : "application/json "}
        self.response = requests.post(url, headers=headers ,auth=(username, password),data=json_data)

    def build_lead(self):

        data = {

  "prospect": {

      "customer": {
          "comments": self.comentario,

          "contacts": [

              {

                  "emails": [

                      {

                          "value": self.email

                      }

                  ],

                  "names": [

                      {

                          "part": "first",

                          "value": self.name

                      }
                  ],

                  "phones": [

                      {

                          "type": "cellphone",

                          "value": self.telefono

                      }

                  ],

              }

          ]

      },

        "vehicles": [

          {

              "make": "Sidway",

              "model": self.producto

          }

        ],

      "provider": {

          "name": {

              "value": 'MeliAPI'

          },

          "service": "Mercado Libre"

      },


  }

}
        return data
