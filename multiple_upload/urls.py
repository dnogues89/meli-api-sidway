from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('upload/', views.fileupload, name = "File_Uploads"),
    path('confirmacion/', views.confirmacion, name='Confirmacion'),
    path('imagenes/', views.image_list_view, name='image_list')
    
]