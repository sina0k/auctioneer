from django.shortcuts import render

from .models import Company, Product, Auction, Transaction, Deal

# Create your views here.


def home (request):
    auctions = Auction.objects.all()
    context = {'auctions': auctions}
    return render(request,'base/home.html',context)