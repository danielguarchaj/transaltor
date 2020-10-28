  
from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'webservice'

urlpatterns = [
    path('translate/', views.TranslateAPIView.as_view(), name='translate'),
    path('top-ten-translations/', views.TopTenTranslatedWordsAPIView.as_view(), name='top-ten-translations'),
    path('failed-translations/', views.FailedTranslationsListAPIView.as_view(), name='failed-translations'),
    path('words/', views.WordListAPIView.as_view(), name='words'),
    path('user/', views.UserAPIView.as_view(), name='user'),
    # path('upload_dictionary/', views.upload_dictionary, name='upload_dictionary'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]