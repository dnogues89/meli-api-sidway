import random

precio = """
Asesores Comerciales certificados por VW Argentina

- Hasta agotar stock en OFERTA
- Consecionario Oficial N°1 por 21 años consecutivos.
- El mejor precio del Mercado Asegurado!
- Acepto permuta por mayor o menor valor.
- Entrega inmediata.
- Disponibilidad de Colores.
- Financiación exclusiva.
- Estacionamiento gratuito.
- Consulte por esta y otras versiones o modelos.
- No incluye ningún gasto.
    
    """

precio = str(precio)[:-1] + str('.'*random.randint(1,9))

print(precio)