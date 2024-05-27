from django.utils import timezone
from datetime import timedelta

# Función para generar las fechas
def generar_fechas(inicio, fin):
    # Convertimos las fechas a objetos datetime
    desde = timezone.datetime.strptime(inicio, "%Y-%m-%d")
    hasta = timezone.datetime.strptime(fin, "%Y-%m-%d")
    
    fechas = []
    
    while desde < hasta:
        # Si la fecha final es menor que "desde + 1 día", ajustamos "hasta" para la última iteración
        siguiente_hasta = min(desde + timedelta(days=1), hasta)
        fechas.append((desde, siguiente_hasta))
        
        # Incrementamos las fechas en 2 días
        desde += timedelta(days=2)
    
    return fechas

# Uso de la función
inicio = "2024-01-01"
fin = "2024-05-27"

fechas_generadas = generar_fechas(inicio, fin)

for desde, hasta in fechas_generadas:
    print(f"Desde: {desde}, Hasta: {hasta}")