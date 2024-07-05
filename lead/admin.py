
from django.contrib import admin

from .models import Lead, Estadisticas,CuitInfo

# Register your models here.
@admin.register(CuitInfo)
class CuitInfoAdmin(admin.ModelAdmin):
    list_display = ['cuit','marca','modelo','tipo','fecha_ultimo_pat','provincia','cliente']
    search_fields = ['cuit','marca','modelo','tipo']
    date_hierarchy = 'fecha_ultimo_pat'


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name','phone','email','item_id','cuenta','contactos','date','to_crm']
    search_fields = ['name', 'phone','email']
    list_filter = ['cuenta']
    ordering = ['-date']
    date_hierarchy = 'date'
    list_per_page = 500

@admin.register(Estadisticas)
class EstadisticasAdmin(admin.ModelAdmin):
    list_display = [
        'cuenta',
        "hoy",
        "ayer",
        "ultimos_3_dias",
        "x_dia_30_dias",
        "total",
    ]
    
    def get_queryset(self, request):
        estadisticas, created = Estadisticas.objects.get_or_create(pk=1)
        estadisticas.actualizar_estadisticas()
        return super().get_queryset(request).filter(pk=1)