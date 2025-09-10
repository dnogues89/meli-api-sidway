from django.shortcuts import render, redirect
from .forms import ImagesForm
from .models import Image
from meli_api.models import GrupoImagenes, Portadas, Modelo

#funcion para bloquear multiples botones
import threading
lock = threading.Lock()
# Decorador para bloquear el acceso al endpoint
def endpoint_lock(func):
    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)
    return wrapper

# Create your views here.
def index(request):
    images = Image.objects.all()
    context = {'images': images}
    return render(request, "index.html", context)

def image_list_view(request):
    images = Image.objects.all()
    return render(request, 'images/image_list.html', {'images': images})

@endpoint_lock 
def fileupload(request):
    portada_id = request.GET.get('portada_id')
    grupo_imagenes = request.GET.get('grupo_imagenes')
    print(f'Portada ID: {portada_id}')
    print(f'grupo_imagenes ID: {grupo_imagenes}')
    
    try:
        modelo = Modelo.objects.get(pk=portada_id)
    except:
        modelo = Modelo.objects.get(pk=grupo_imagenes)
    retorno = request.environ['HTTP_REFERER']
    
    form = ImagesForm(request.POST, request.FILES)
    if grupo_imagenes:
        if request.method == 'POST':
            images = request.FILES.getlist('pic')
            
            try:
                g_imagenes = GrupoImagenes.objects.get(pk=modelo.g_imagenes.pk)
            except:
                g_imagenes = GrupoImagenes.objects.create(codigo = modelo.espasa_db.codigo, nombre = form.data['model'])
                g_imagenes.save()
                
            for image in images:
                image_ins = Image.objects.create(model_code=modelo.espasa_db.codigo, model=form.data['model'], pic = image)
                image_ins.save()
                g_imagenes.imagenes.add(image_ins)
            g_imagenes.save()
            
            modelo.g_imagenes = g_imagenes
            modelo.save()
            return redirect('/admin/meli_api/modelo/')
        
    if portada_id:
        print('estoy en portadas')
        if request.method == 'POST':
            images = request.FILES.getlist('pic')
            
            try:
                portadas = Portadas.objects.get(pk=modelo.portadas.pk)
            except:
                portadas = Portadas.objects.create(codigo = modelo.espasa_db.codigo, nombre = form.data['model'])
                portadas.save()
                
            for image in images:
                image_ins = Image.objects.create(model_code=modelo.espasa_db.codigo, model=form.data['model'], pic = image)
                image_ins.save()
                portadas.imagenes.add(image_ins)
            portadas.save()
            
            modelo.portadas = portadas
            modelo.save()
            
            return redirect('/admin/meli_api/modelo/')
    context = {'form': form}
    return render(request, "upload.html", context)

def confirmacion(request):
    return render(request, 'confirmacion.html')


def galeria(request):
    grupos = GrupoImagenes.objects.all()
    portadas = Portadas.objects.all()

    grupo_id = request.GET.get('grupo')
    portada_id = request.GET.get('portada')

    if grupo_id:
        imagenes = GrupoImagenes.objects.get(id=grupo_id).imagenes.all()
    elif portada_id:
        imagenes = Portadas.objects.get(id=portada_id).imagenes.all()
    else:
        imagenes = Image.objects.none()

    context = {
        'grupos': grupos,
        'portadas': portadas,
        'imagenes': imagenes,
        'grupo_seleccionado': int(grupo_id) if grupo_id else None,
        'portada_seleccionada': int(portada_id) if portada_id else None
    }
    return render(request, 'galeria.html', context)