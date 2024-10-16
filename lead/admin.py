
from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Lead, Estadisticas,CuitInfo, Usado

# Register your models here.
@admin.register(CuitInfo)
class CuitInfoAdmin(ModelAdmin):
    list_display = ['cuit','marca','modelo','tipo','fecha_ultimo_pat','provincia','cliente']
    search_fields = ['cuit','marca','modelo','tipo']
    date_hierarchy = 'fecha_ultimo_pat'

@admin.register(Usado)
class UsadoAdmin(ModelAdmin):
    list_display = ['marca','modelo','anio','cerokm','compra','venta','tipo_compra','tipo_acreedor','acreedor']
    

@admin.register(Lead)
class LeadAdmin(ModelAdmin):
    list_display = ['name','phone','email','item_id','cuenta','contactos','date','c_info','to_crm']
    search_fields = ['name', 'phone','email']
    list_filter = ['cuenta']
    ordering = ['-date']
    date_hierarchy = 'date'
    list_per_page = 500
    
    def c_info(self, obj):
        try:
            return f"{obj.cuit_info.marca} | {obj.cuit_info.modelo} | {obj.cuit_info.fecha_ultimo_pat.strftime('%m/%y')}"
        except:
            return '-'

@admin.register(Estadisticas)
class EstadisticasAdmin(ModelAdmin):
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