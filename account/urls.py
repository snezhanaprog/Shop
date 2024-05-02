from django.urls import path
from . import views

urlpatterns = [
    path('', views.authorization, name='authorization'),
    path('registration/', views.registration, name='registration'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path("log-out/", views.log_out, name='exit'),
]