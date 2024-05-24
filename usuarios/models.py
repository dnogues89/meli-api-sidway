from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Cuenta(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    meli_id = models.CharField(max_length=10, null=True)
    
    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
    
    def __str__(self) -> str:
        return self.name