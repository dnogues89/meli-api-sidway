import requests
import json

# Primera conexion
# https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id=2164447249478080&redirect_uri=https://espasa.dnoguesdev.com.ar


class MeliAPI():
    def __init__(self,data) -> None:       
        self.data = data

    def get_code_tg(self): #Esta funcion no funciona todavia
        url = 'https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id=2164447249478080&redirect_uri=https://espasa.dnoguesdev.com.ar'
        
        response = requests.request("GET",url,allow_redirects=False)
        
        return response
        
    def auth_token(self):
        url = "https://api.mercadolibre.com/oauth/token"

        payload = f'grant_type=authorization_code&client_id={self.data.app_id}&client_secret={self.data.client_secret}&code={self.data.code_tg}&redirect_uri={self.data.url}&code_verifier=$CODE_VERIFIER'
        headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return response
        
    def renew_token(self):

        url = "https://api.mercadolibre.com/oauth/token"

        payload = f'grant_type=refresh_token&client_id={self.data.app_id}&client_secret={self.data.client_secret}&refresh_token={self.data.refresh_secret}'
        headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return response

    def items_by_id(self, user_id):
        
        url = f'https://api.mercadolibre.com/users/{user_id}/items/search'

        headers = {
        'Authorization': f'Bearer {self.data.access_token}'
        }
        
        response = requests.request("GET", url,headers=headers)
        
        return response

    def items_por_usuario_categoria(self,user_id):
        
        url = f'https://api.mercadolibre.com/sites/MLA/search?seller_id={user_id}&category={categoria}'

        headers = {
        'Authorization': f'Bearer {self.data.access_token}'
        }  
        
        return requests.request("GET", url)

    def publicar_auto(self,payload):
        url = "https://api.mercadolibre.com/items"

        # payload = ArmarPublicacion().pub(632,2024,'Pub desde Python - Taos Comfortline',25123123,'gold')
        headers = {
        'Authorization': f'Bearer {self.data.access_token}',
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        
        return response

    def cambiar_desc(self,pub,desc):
        url = f"https://api.mercadolibre.com/items/{pub}/description?api_version=2"

        payload = json.dumps({
        "plain_text": desc
        })
        headers = {
        'Authorization': f'Bearer {self.data.access_token}',
        'Content-Type': 'application/json'
        }

        response = requests.request("PUT", url, headers=headers, data=payload)

        return response
        
    def consulta_pub(self,pub_id):
        url = f"https://api.mercadolibre.com/items/{pub_id}"

        headers = {
        'Authorization': f'Bearer {self.data.access_token}'
        }

        response = requests.request("GET", url)

        return response
    
    def pausar_eliminar_publicacion(self,pub_id,status):
        key = "status"
        if status == 'delete':
            key = "deleted"
            status = "true"
            
        url = f"https://api.mercadolibre.com/items/{pub_id}"

        payload = json.dumps({key: status})
        headers = {
        'Authorization': f'Bearer {self.data.access_token}',
        'Content-Type': 'application/json'
        }

        response = requests.request("PUT", url, headers=headers, data=payload)
        
        return response  
    
    def actualizar_precio(self,pub_id,precio):
        url = f"https://api.mercadolibre.com/items/{pub_id}"

        payload = json.dumps({'price': precio})
        headers = {
        'Authorization': f'Bearer {self.data.access_token}',
        'Content-Type': 'application/json'
        }

        response = requests.request("PUT", url, headers=headers, data=payload)
        
        return response  
    
    def get_user_me(self):
        url = "https://api.mercadolibre.com/users/me"
        headers = {
        'Authorization': f'Bearer {self.data.access_token}',
        }       
        
        response = requests.request("GET", url, headers=headers)
        
        return response  
        
    def views_by_item(self, item, desde, hasta):
        url = f"https://api.mercadolibre.com/items/visits?ids={item}&date_from={desde}&date_to={hasta}"
        headers = {
        'Authorization': f'Bearer {self.data.access_token}',
        } 

        response = requests.request("GET", url, headers=headers)

        return response
    
    def phone_by_items(self, items:list, hasta):
        url = f"https://api.mercadolibre.com/items/contacts/phone_views/time_window?ids={items}&last=30&unit=day&ending={hasta}"

        headers = {
        'Authorization': f'Bearer {self.data.access_token}',
        } 

        response = requests.request("GET", url, headers=headers)

        return response
    
    def preguntas(self, user_id):
        
        url = f"https://api.mercadolibre.com/questions/search?seller_id={user_id}&api_version=4"
        
        headers = {
        'Authorization': f'Bearer {self.data.access_token}',
        } 

        response = requests.request("GET", url, headers=headers)

        return response
    
    def responder_pregunta(self, question_id, answer):
        
        url = f"https://api.mercadolibre.com/answers"
        
        headers = {
        'Authorization': f'Bearer {self.data.access_token}',
        }
        
        payload = json.dumps({
                                "question_id": question_id, 
                                "text":answer 
                                })
    
        response = requests.request("POST", url, headers=headers, data=payload)
        
        return response  
    
    def leads(self, user_id, desde = "",hasta=""):
        url = f"https://api.mercadolibre.com/vis/users/{user_id}/leads/buyers?date_from={desde}&date_to={hasta}&limit=100"
        
        headers = {
        'Authorization': f'Bearer {self.data.access_token}',
        } 

        response = requests.request("GET", url, headers=headers)

        return response
