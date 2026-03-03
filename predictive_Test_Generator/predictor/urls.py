from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('predict/', views.predict, name='predict'),
    path('add-word/', views.add_word, name='add_word'),
]