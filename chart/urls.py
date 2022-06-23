
from django.urls import path
from django.conf.urls import include
from . import views

app_name = 'chart'

urlpatterns = [
    path('bar/', views.ChartView.as_view(), name='bar'),
    path('index/', views.IndexView.as_view(), name='index'),
]
