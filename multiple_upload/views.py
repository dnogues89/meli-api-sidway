from django.shortcuts import render, redirect
from .forms import ImagesForm
from .models import Image
from meli_api.models import GrupoImagenes

# Create your views here.
def index(request):
    images = Image.objects.all()
    context = {'images': images}
    return render(request, "index.html", context)


def fileupload(request):
    form = ImagesForm(request.POST, request.FILES)
    if request.method == 'POST':
        images = request.FILES.getlist('pic')
        try:
            g_imagenes = GrupoImagenes.objects.get(codigo = form.data['model_code'])
        except:
            g_imagenes = GrupoImagenes.objects.create(codigo = form.data['model_code'], nombre = form.data['model']).save()
        g_imagenes = GrupoImagenes.objects.get(codigo = form.data['model_code'])
        for image in images:
            print(form.data['model_code'])
            print(image)
            image_ins = Image.objects.create(model_code=form.data['model_code'], model=form.data['model'], pic = image)
            image_ins.save()
            g_imagenes.imagenes.add(image_ins)
        g_imagenes.save()
        return redirect('admin:index')
    context = {'form': form}
    return render(request, "upload.html", context)