from django.contrib import admin
from .models import Image
from unfold.admin import ModelAdmin

# Register your models here.
@admin.register(Image)
class ImageAdmin(ModelAdmin):
    list_display =['model_code','model','pic']