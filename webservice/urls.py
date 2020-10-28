  
from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'webservice'

urlpatterns = [
    path('translate/', views.TranslateAPIView.as_view(), name='translate'),
    path('user/', views.UserAPIView.as_view(), name='user'),
    # path('upload_dictionarie/', views.upload_dictionarie, name='upload_dictionarie'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]