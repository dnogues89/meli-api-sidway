from django.db import models
from django.contrib.auth.models import User

# Create your models here.
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
    
    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
    
    def __str__(self) -> str:
        return self.name
    
    
