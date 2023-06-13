from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Q

from .tasks import createNewTaskForAuction
from .models import Company, Product, Auction, Transaction, Deal, User, Bid, BID_STEP, ShoppingCart, BuyingProduct
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserForm, MyUserCreationForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.conf import settings
import requests
import json


ZP_API_REQUEST = f"https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://sandbox.zarinpal.com/pg/StartPay/"

CallbackURL = 'http://127.0.0.1:8000/verify-payment/'


@login_required(login_url='login')
def send_request(request):
    amount = 0
    description = ""
    for p in request.user.shopping_cart.products.all():
        amount += p.product.price * p.quantity
        description += f"{p.product.name} x {p.quantity} - \n"
    
    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": float(amount),
        "Description": description,
        "CallbackURL": CallbackURL,
    }
    data = json.dumps(data)
    # set content length by data
    headers = {'content-type': 'application/json', 'content-length': str(len(data)) }
    try:
        response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)

        if response.status_code == 200:
            response = response.json()
            if response['Status'] == 100:
                return redirect(ZP_API_STARTPAY + str(response['Authority']))
            else:
                return JsonResponse({'status': False, 'code': str(response['Status'])})
        return HttpResponse(response)
    
    except requests.exceptions.Timeout:
        return JsonResponse({'status': False, 'code': 'timeout'})
    except requests.exceptions.ConnectionError:
        return JsonResponse({'status': False, 'code': 'connection error'})

@login_required(login_url='login')
def verify(request):
    authority = request.GET.get('Authority', '')
    amount = 0
    for p in request.user.shopping_cart.products.all():
        amount += p.product.price * p.quantity
    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": float(amount),
        "Authority": authority,
    }
    data = json.dumps(data)
    # set content length by data
    headers = {'content-type': 'application/json', 'content-length': str(len(data)) }
    response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

    if response.status_code == 200:
        response = response.json()
        if response['Status'] == 100:
            paymentRefID = response["RefID"]
            # TODO create deal with this ref id and products in the shopping_cart then empty the shopping cart.

            # return JsonResponse({'status': True, 'RefID': response['RefID']})
            return render(request, 'base/done-payment.html', { "success": True, "refID": paymentRefID })
        else:
            return render(request, 'base/done-payment.html', { "success": False })
    return HttpResponse(response)

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

    if request.user.is_authenticated:
        active_auctions = Auction.objects.filter(bids__user=request.user, end_time=None).distinct()
    else:
        active_auctions = None
    context = {'auctions': auctions, 'active_auctions': active_auctions}
    return render(request, 'base/home.html', context)


@login_required(login_url='login')
def checkout(request):
    if request.method == "POST":
        print('need to checkout')
    return render(request, 'base/checkout.html', {})


@login_required(login_url='login')
def createBidHomePage(request, auctionId):
    if request.method == 'POST':
        createBid(auctionId, request.user)

        return redirect('/')


def createBid(auctionId, user):
    # TODO throw exceptions instead of returning HttpResponse, & catch them in caller functions
    try:
        auction = Auction.objects.get(id=auctionId)
    except ObjectDoesNotExist:
        return HttpResponse('Auction not found!', status=404)
    # if auction.start_time > timezone.now():
    #     return HttpResponse('Auction has not started', status=400)
    # if auction.end_time:
    #     return HttpResponse('Auction has ended!', status=400)
    # if auction.last_bid and user.id == auction.last_bid.user.id:
    #     return HttpResponse("You already are the last bidder in this auction!", status=400)

    bid = Bid.objects.create(
        auction=auction,
        user=user,
        price=auction.current_price
    )

    auction.current_price += BID_STEP
    auction.last_bid = bid

    bid.save()
    auction.save()
    createNewTaskForAuction(auction)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'auction_%s' % auction.id,
        {
            'type': 'new_bid',
            'data': {
                'name': bid.user.username,
                'id': bid.user.id,
                'created_at': bid.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'price': float(auction.current_price)
            }
        }
    )


def addToCart(product_id, user):
    try:
        user.shopping_cart
    except:
        ShoppingCart.objects.create(user=user)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return HttpResponse('Product not found!', status=404)

    buying_product, created = BuyingProduct.objects.get_or_create(
        product=product,
        cart=user.shopping_cart,
        defaults={'quantity': 1}
    )

    if not created:
        buying_product.quantity += 1
        buying_product.save()

    return HttpResponse('Item added to cart successfully!')


def auction(request, pk):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('/login/')
        action = request.POST.get('action')
        if action == 'bid':
            createBid(pk, request.user)
        elif action == 'buy':
            addToCart(request.POST.get('product'), request.user)

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
