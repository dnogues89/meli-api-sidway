from typing import Any
from django.db import models

# Create your models here.
class Image(models.Model):
    model_code = models.CharField(max_length=9, default='', verbose_name='Codigo Modelo')
    model = models.CharField(max_length=50, default='',verbose_name='Modelo')
    pic = models.FileField(upload_to='MiniApp_Images')
    asd = models.ImageField(default=0)
    
    def __str__(self) -> str:
        return f'{self.model_code} | {self.model}'

    def delete(self,*args,**kwargs):
        self.pic.delete()
        super().delete(*args,**kwargs)