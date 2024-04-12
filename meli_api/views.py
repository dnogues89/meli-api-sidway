from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import models
import json

# Create your views here.
def mis_pubs(request):
    return HttpResponse('Archivo no encontrado.')