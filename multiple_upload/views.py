from django.shortcuts import render, redirect
from .forms import ImagesForm
from .models import Image

# Create your views here.
def index(request):
    images = Image.objects.all()
    context = {'images': images}
    return render(request, "index.html", context)


def fileupload(request):
    form = ImagesForm(request.POST, request.FILES)
    if request.method == 'POST':
        images = request.FILES.getlist('pic')
        for image in images:
            print(form.data['model_code'])
            image_ins = Image(model_code=form.data['model_code'], model=form.data['model'], pic = image)
            image_ins.save()
        return redirect('admin:index')
    context = {'form': form}
    return render(request, "upload.html", context)