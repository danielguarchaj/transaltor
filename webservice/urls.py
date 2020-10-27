  
from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'webservice'

urlpatterns = [
    path('translate/', views.TranslateAPIView.as_view(), name='translate')
]