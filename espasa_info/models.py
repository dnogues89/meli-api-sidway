from django.db import models

def convertir_precio(precio):
    try:
        return int(precio)
    except:
        try:
            return int(precio.replace('$','').replace('.','').strip())
        except:
            return 0

# Create your models here.
class CRM(models.Model):
    codigo = models.CharField(max_length=10)
    desc = models.CharField(max_length=100,default=0,null=True,blank=True)
    familia = models.CharField(max_length=100,default=0,null=True,blank=True)
    precio_lista = models.CharField(max_length=100,default=0,null=True,blank=True)
    impuestos_internos = models.CharField(max_length=100,default=0,null=True,blank=True)
    precio_tx = models.CharField(max_length=100,default=0,null=True,blank=True)
    stock = models.CharField(max_length=100,default=0,null=True,blank=True)
    ofertas = models.CharField(max_length=100,default=0,null=True,blank=True)
    oferta_min = models.CharField(max_length=100,default=0,null=True,blank=True)
    oferta_max = models.CharField(max_length=100,default=0,null=True,blank=True)
    
    def __str__(self) -> str:
        return f'{self.codigo} | {self.desc}'
    
    class Meta:
        verbose_name = 'Actualizar Stock y precios'
        verbose_name_plural = 'Actualizar Stock y precios'
    
    def save(self, *args, **kwargs):
        self.precio_tx = convertir_precio(self.precio_tx)
        self.precio_tx = "$ {:,.0f}".format(self.precio_tx).replace(",", ".")
        
        self.oferta_min = convertir_precio(self.oferta_min)
        self.oferta_min = "$ {:,.0f}".format(self.oferta_min).replace(",", ".")
        
        self.oferta_max = convertir_precio(self.oferta_max)
        self.oferta_max = "$ {:,.0f}".format(self.oferta_max).replace(",", ".")

        super().save()