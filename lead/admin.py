from django.contrib import admin
from .models import Lead

# Register your models here.
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name','phone','email','item_id','contactos','date','to_crm']
    search_fields = ['name', 'phone','email']
    ordering = ['-date']
    date_hierarchy = 'date'
    list_per_page = 500