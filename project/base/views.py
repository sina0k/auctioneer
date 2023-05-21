from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q

from .tasks import createNewTaskForAuction
from .models import Company, Product, Auction, Transaction, Deal, User, Bid, BID_STEP
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserForm, MyUserCreationForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone


# Create your views here.

def loginPage(request):
    page = 'login'
    context = {'page': page}

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit')

        return redirect('home')

    return render(request, 'base/login_register.html', context)


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})


def logoutUser(request):
    logout(request)
    return redirect('home')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    auctions = Auction.objects.filter(
        Q(product__name__icontains=q) |
        Q(product__company__name__icontains=q) |
        Q(product__description__icontains=q)
    )

    won_deals = Deal.objects.filter(deal_type='Auction')[:10]
    auction_count = auctions.count()
    context = {'auctions': auctions, 'auction_count': auction_count, 'won_deals': won_deals}
    return render(request, 'base/home.html', context)


@login_required(login_url='login')
def createBid(request, auctionId):
    if request.method == 'POST':
        try:
            auction = Auction.objects.get(id=auctionId)
        except ObjectDoesNotExist:
            return HttpResponse('Auction not found!', status=404)
        # TODO validate if auction start time has arrived or auction is closed
        if auction.last_bid and request.user.id == auction.last_bid.user.id:
            return HttpResponse("You already are the last bidder in this auction!", status=400)

        bid = Bid.objects.create(
            auction=auction,
            user=request.user,
            price=auction.current_price
        )

        auction.current_price += BID_STEP
        auction.last_bid = bid

        bid.save()
        auction.save()
        createNewTaskForAuction(auction)

        return redirect(f'/auction/{auctionId}/')



def auction(request, pk):
    auction = Auction.objects.get(id=pk)
    context = {'auction': auction}
    return render(request, 'base/auction.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    deals = user.deals.all()
    bids = user.bids.all()
    owner_user = user == request.user
    context = {'user': user, 'owner_user': owner_user, 'deals': deals, 'bids': bids}
    return render(request, 'base/profile.html', context)


def about(request):
    return render(request, 'base/about.html', {})


def learn(request):
    return render(request, 'base/learn.html', {})


def winners(request):
    now = timezone.now()
    start_time = now - timedelta(hours=24)

    deals_within_a_day = Deal.objects.filter(Q(deal_type='Auction')
                                             & Q(date_modified__range=(start_time, now)))
    context = {'won_deals': deals_within_a_day}
    return render(request, 'base/winners.html', context)


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserUpdateForm(instance=user)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update_user.html', {'form': form})
