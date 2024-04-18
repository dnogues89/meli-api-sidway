from django.contrib import admin
from .models import Image


# Register your models here.
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    fields =['model_code','model']