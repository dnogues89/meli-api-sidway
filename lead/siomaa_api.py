import requests
from .siomaa_key import SIOMAA_USER, SIOMAA_PASSWORD, SIOMA_ENDPOING
import json

class Sioma_API():
    def __init__(self,cuit) -> None:
        self.cuit = cuit
        self.payload = self.get_payload()
    
    def get_payload(self):
        return {
        "Usuario": SIOMAA_USER,
        "Password": SIOMAA_PASSWORD,
        "Consultas": [
        {
        "CUIT": self.cuit
        }
        ]
        }
        
        
    def get_data(self):
        try:
            return requests.post(SIOMA_ENDPOING,data= json.dumps(self.payload),headers={"Content-Type": "application/json"}).json()[0]
        except:
            return None
    

api = Sioma_API(23342509509).get_data()
if api:
    print(api["HistoricoCompras"])