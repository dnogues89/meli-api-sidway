"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('mis_pubs/',views.mis_pubs, name='mis_pubs'),
    path('get_stats/',views.update_stats, name='update_stats'),
    path('sincro_meli/',views.sincro_meli, name='sincro_meli'),
    path('preguntas/',views.preguntas, name='preguntas'),
    path('publicacion/<str:publicacion>',views.publicacion, name='publicacion'),
    path('publicar/',views.publicar_v2, name='publicacionv2'),
    path('eliminar/',views.eliminar_pubs, name='eliminar'),
    path('activa/',views.activa, name='activa'),
    path('republicar/', views.republicar, name='republicar'),
    path('seatch_page/',views.search_page, name='search_page')
    
]
