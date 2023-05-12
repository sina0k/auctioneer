from django.shortcuts import render

from .models import Company, Product, Auction, Transaction, Deal

# Create your views here.


def home (request):
    return render(request,'home.html')