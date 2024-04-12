# Definir las listas
lista1 = [1, 2, 3, 4, 4, 5]
lista2 = [4, 5, 6, 7, 8, 8]

# Convertir las listas en conjuntos para eliminar duplicados
set1 = set(lista1)
set2 = set(lista2)

# Encontrar los elementos únicos que están en una lista pero no en la otra
unicos_en_lista1_no_en_lista2 = set1 - set2
unicos_en_lista2_no_en_lista1 = set2 - set1

print("Elementos únicos en lista 1 pero no en lista 2:", unicos_en_lista1_no_en_lista2)
print("Elementos únicos en lista 2 pero no en lista 1:", unicos_en_lista2_no_en_lista1)
print(type(unicos_en_lista1_no_en_lista2))

for i in unicos_en_lista1_no_en_lista2:
    print(i)
    print(type(i))