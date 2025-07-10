import requests
from bs4 import BeautifulSoup


class PaginaPublicacion:
    def __init__(self,modelo,publicacion='') -> None:
        self.modelo = modelo
        self.desde = 0
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            )
        }
        self.url = f"https://autos.mercadolibre.com.ar/{self.modelo.replace(' ','-')}_Desde_{self.desde}_NoIndex_True"
        self.html = requests.get(self.url, headers=self.headers).text
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.productos = []
        self.publicacion = publicacion
        self.precio = {}

    def total_pages(self):
        try:
            return int(self.soup.find(class_='andes-pagination__page-count').text.split()[-1])
        except:
            return 1
    
    def next_page(self):
        if self.soup.find(string='Siguiente'):
            print()
            self.desde += 48
            self.url = f"https://autos.mercadolibre.com.ar/{self.modelo.replace(' ','-')}_Desde_{self.desde}_NoIndex_True"
            print(self.url)
            return True
        else:
            return False
        
    def validate_info(self,param):
        try:
            param
            return param
        except:
            return None

    def get_page_products(self):      
        self.posicion = 0
        print(self.url)
        for producto in self.soup.find_all(class_="ui-search-result__wrapper"):
            url = self.validate_info(producto.find('a')['href'])
            id_pub = self.validate_info(url.split("MLA-")[1].split("-")[0])
            id_pub = f"MLA{id_pub}"
            print(id_pub)
            self.posicion += 1
            if self.publicacion == id_pub:
                print('La encontre')
                return True

            
    def search_page(self):
        last_page = 0 #para que la ultima pagina no corte el bucle
        page = 0
        while self.next_page() != False or last_page == 0:
            if self.get_page_products():
                return page, self.posicion
                break
            try:
                self.soup.find(string='Siguiente').parent.parent
            except:
                last_page = 1
                pass
            try:
                self.html = requests.get(self.url, headers=self.headers).text
                self.soup = BeautifulSoup(self.html, 'html.parser')
            except:
                break
            page +=1
        return 0, 0
    
    def titulo(self):
        try:
            #EL titulo mas comun
            from collections import Counter
            autos = []
            for producto in self.soup.find_all(class_='ui-search-result__wrapper'):
                prod = producto.find_next('a')
    
                auto = {'titulo':prod.text, 'url':prod['href']}
                autos.append(auto)
            
            # Contar ocurrencias de cada título
            titulos = [auto['titulo'] for auto in autos]
            conteo = Counter(titulos)

            # Obtener el título más común
            titulo_mas_comun, _ = conteo.most_common(1)[0]

            # Buscar una URL asociada a ese título
            url_asociada = next(auto['url'] for auto in autos if auto['titulo'] == titulo_mas_comun)

            # Resultado
            return " ".join(titulo_mas_comun.split(' ')[1:])
        except Exception as e:
            from .models import Errores
            error = Errores.objects.create(
                error=str(e),
                name='Error al obtener el titulo de la publicacion',
            )
            error.save()
            return self.modelo
        

    
    
    
if __name__ == '__main__':
    app = PaginaPublicacion('amarok highline','MLA2151677714')
    print(app.search_page())
    
        
