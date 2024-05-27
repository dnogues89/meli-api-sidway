from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Cuenta(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    code_tg = models.CharField(max_length=300)
    token = models.CharField(max_length=300)
    refresh_secret = models.CharField(max_length=300)
    meli_id = models.CharField(max_length=10, null=True)
    
    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
    
    def __str__(self) -> str:
        return self.name