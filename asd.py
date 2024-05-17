def convertir_numero(numero):
    numero = numero.replace('-15-','').replace(' ','').replace('-','')
    numero = numero if numero[0] != '0' else numero [1:]
    return numero

convertir_numero('02342 454932')   