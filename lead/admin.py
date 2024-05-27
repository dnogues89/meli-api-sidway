from django.contrib import admin
from .models import Lead

# Register your models here.
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name','phone','email','item_id','contactos','date']
    search_fields = ['name', 'phone','email']
    date_hierarchy = 'date'
    list_per_page = 500