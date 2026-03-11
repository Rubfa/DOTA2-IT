from django.urls import path
from . import views

app_name = 'visualisation'

urlpatterns = [
    path('', views.index, name='index'),
]