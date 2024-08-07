from django.contrib import admin
from .models import Image
from unfold.admin import ModelAdmin

# Register your models here.
@admin.register(Image)
class ImageAdmin(ModelAdmin):
    fields =['model_code','model']