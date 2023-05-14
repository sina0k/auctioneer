from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Company, Product, Auction, Transaction, Deal


# Create your views here.


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    auctions = Auction.objects.filter(
        Q(product__name__icontains=q) |
        Q(product__company__name__icontains=q) |
        Q(product__description__icontains=q)
    )
    context = {'auctions': auctions}
    return render(request, 'base/home.html', context)


def auction(request, pk):
    auction = Auction.objects.get(id=pk)
    context = {'auction': auction}
    return render(request, 'base/auction.html', context)
