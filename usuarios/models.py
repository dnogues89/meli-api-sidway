from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class PublicacionConfig(models.Model):
    name = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    descripcion = models.TextField()
    telefono_sucursal = models.CharField(max_length=100)
    email_sucursal = models.EmailField()
    whatsapp = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Publicación Config'
        verbose_name_plural = 'Publicaciones Config'
    
    def __str__(self) -> str:
        return self.name

class Cuenta(models.Model):
    name = models.CharField(max_length=100)
    app_id = models.CharField(max_length = 30, default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    code_tg = models.CharField(max_length=300)
    token = models.CharField(max_length=300)
    url = models.CharField(max_length = 100, default=0)
    client_secret = models.CharField(max_length = 100, default=0)
    refresh_secret = models.CharField(max_length=300, default=0)
    access_token = models.CharField(max_length = 100, default=0)
    user_meli = models.CharField(max_length=50, default='')
    salesforce_group = models.CharField(max_length=10, null=True, blank=True, default='')
    publicacion_config = models.ForeignKey(PublicacionConfig, on_delete=models.SET_NULL)
    
    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
    
    def __str__(self) -> str:
        return self.name
    
    
