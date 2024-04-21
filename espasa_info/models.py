from django.db import models



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