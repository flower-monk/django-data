import json

import markdown
from django.contrib.auth.models import User
from random import randrange

from django.db.models import Q
from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from django.core.paginator import Paginator

from django.views.generic import DetailView
from django.views.generic import ListView

def index(request):
    context = {}
    return render(request, 'index.html', context)