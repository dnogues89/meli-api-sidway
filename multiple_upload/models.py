from typing import Any
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Create your models here.
class Image(models.Model):
    model_code = models.CharField(max_length=10, default='', verbose_name='Codigo Modelo')
    model = models.CharField(max_length=100, default='',verbose_name='Modelo')
    pic = models.FileField(upload_to='MiniApp_Images')
    asd = models.ImageField(default=0)
    
    def __str__(self) -> str:
        return f'{self.model_code} | {self.model}'
    
@receiver(pre_delete, sender=Image)
def image_delete(sender, instance, **kwargs):
    instance.pic.delete(False)
