import requests
from bs4 import BeautifulSoup


class PaginaPublicacion:
    def __init__(self,modelo,publicacion) -> None:
        self.modelo = modelo
        self.desde = 0
        self.url = f"https://autos.mercadolibre.com.ar/{self.modelo.replace(' ','-')}_Desde_{self.desde}_NoIndex_True"
        self.html = requests.get(self.url).text
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
        for producto in self.soup.find_all(class_="ui-search-result__wrapper"):
            url = self.validate_info(producto.find('a')['href'])
            id_pub = self.validate_info(url.split("MLA-")[1].split("-")[0])
            id_pub = f"MLA{id_pub}"
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
                self.html = requests.get(self.url).text
                self.soup = BeautifulSoup(self.html, 'html.parser')
            except:
                break
            page +=1
        return 0, 0

if __name__ == '__main__':
    app = PaginaPublicacion('Nivus Highline','MLA1495451565')
    print(app.search_page())
    # print(app.url)
    
        
