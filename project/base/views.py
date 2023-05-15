from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Company, Product, Auction, Transaction, Deal, User, Bid
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserForm, MyUserCreationForm


# Create your views here.

def loginPage(request):
    page = 'login'
    context = {'page': page}

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        # try:
        #     user = User.objects.get(username=username)
        # except:
        #     messages.error(request, 'User does not exist')
        #
        # if user.check_password(password):
        #     context.update({'user': user})
        #     login(request, user)
        #     return redirect(request, 'base/home.html', context)
        #
        # else:
        #     messages.error(request, 'Username OR password does not exit')

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


def auction(request, pk):
    auction = Auction.objects.get(id=pk)
    context = {'auction': auction}
    return render(request, 'base/auction.html', context)
