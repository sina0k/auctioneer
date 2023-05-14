from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = "home" ),
    path('auction/<str:pk>/', views.auction, name="auction"),
]
