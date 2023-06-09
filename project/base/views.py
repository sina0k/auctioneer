from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Q

from .tasks import createNewTaskForAuction
from .models import Company, Product, Auction, Transaction, Deal, User, Bid, BID_STEP, ShoppingCart, BuyingProduct, \
    DealType, BID_PRICE
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import MyUserCreationForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.conf import settings
import requests
import json

ZP_API_REQUEST = f"https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://sandbox.zarinpal.com/pg/StartPay/"

verifyCallbackURL = 'http://127.0.0.1:8000/verify-payment/'
verifyAuctionCallbackURL = 'http://127.0.0.1:8000/verify-auction-payment/'
verifyTokenBuyCallbackURL = 'http://127.0.0.1:8000/verify-token-payment/'


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
        "CallbackURL": verifyCallbackURL,
    }
    data = json.dumps(data)
    # set content length by data
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
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
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
    response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

    if response.status_code == 200:
        response = response.json()
        if response['Status'] == 100:
            paymentRefID = response["RefID"]

            transaction = Transaction.objects.create(
                payment_number=paymentRefID,
                price=amount
            )

            cart = request.user.shopping_cart

            cart.user = None
            cart.save()

            request.user.shopping_cart = None
            ShoppingCart.objects.create(user=request.user)

            Deal.objects.create(
                cart=cart,
                user=request.user,
                deal_type=DealType.BUY.value,
                transaction=transaction,
            )

            return render(request, 'base/done-payment.html', {"success": True, "refID": paymentRefID})
        else:
            return render(request, 'base/done-payment.html', {"success": False})
    return HttpResponse(response)


@login_required(login_url='login')
def auctionPayment(request, pk):
    auction = Auction.objects.get(id=pk)

    if auction.has_paid:
        return HttpResponse("this is already payed!")

    if auction.last_bid.user.id != request.user.id:
        return HttpResponse("You can't pay for this!")

    amount = auction.current_price - BID_STEP
    description = f"{auction.product.name} x {1} - won in auction!"

    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": float(amount),
        "Description": description,
        "CallbackURL": verifyAuctionCallbackURL + f"{pk}/",
    }
    data = json.dumps(data)
    # set content length by data
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
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
def verifyAuctionPayment(request, pk):
    auction = Auction.objects.get(id=pk)
    authority = request.GET.get('Authority', '')
    amount = auction.current_price - BID_STEP
    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": float(amount),
        "Authority": authority,
    }
    data = json.dumps(data)
    # set content length by data
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
    response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

    if response.status_code == 200:
        response = response.json()
        if response['Status'] == 100:
            paymentRefID = response["RefID"]

            auction.has_paid = True
            auction.save()

            transaction = Transaction.objects.create(
                payment_number=paymentRefID,
                price=amount
            )

            cart = ShoppingCart.objects.create()

            BuyingProduct.objects.create(
                product=auction.product,
                quantity=1,
                cart=cart
            )

            Deal.objects.create(
                cart=cart,
                user=request.user,
                deal_type=DealType.AUCTION.value,
                transaction=transaction,
            )

            return render(request, 'base/done-payment.html', {"success": True, "refID": paymentRefID})
        else:
            return render(request, 'base/done-payment.html', {"success": False})
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
            context["error"] = "نام کاربری یا رمز عبور صحیح نیست!"

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
    error = request.GET.get('error')

    q = request.GET.get('q') if request.GET.get('q') != None else ''
    now = timezone.now()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('/login/')
        addToCart(request.POST.get('product'), request.user)

    auctions = Auction.objects.filter(
        Q(product__name__icontains=q) |
        Q(product__company__name__icontains=q) |
        Q(product__description__icontains=q)
    ).exclude(
        end_time__lt=now - timedelta(hours=2)
    )
    if request.user.is_authenticated:
        won_auctions = Auction.objects.exclude(end_time=None).filter(last_bid__user=request.user).exclude(
            has_paid=True).distinct()
        active_auctions = Auction.objects.filter(bids__user=request.user, end_time=None).distinct()
    else:
        won_auctions = None
        active_auctions = None
    context = {'auctions': auctions, "active_auctions": active_auctions, 'won_auctions': won_auctions,
               'BID_STEP': -BID_STEP, "error": error}
    return render(request, 'base/home.html', context)


@login_required(login_url='login')
def checkout(request):
    if request.method == "POST":
        print('need to checkout')
    return render(request, 'base/checkout.html', {})


def product_list(request):
    context = {'products': Product.objects.all()}
    return render(request, 'base/product_list.html', context)


@login_required(login_url='login')
def createBidHomePage(request, auctionId):
    if request.method == 'POST':
        try:
            createBid(auctionId, request.user)
        except Exception as e:
            return redirect(f'/?error={str(e)}')

        return redirect('/')


def createBid(auctionId, user):
    try:
        auction = Auction.objects.get(id=auctionId)
    except ObjectDoesNotExist:
        raise Exception("مزایده وجود ندارد!") # TODO define NotFoundException
    if auction.start_time > timezone.now():
        raise Exception('مزایده آغاز نشده است!')
    if auction.end_time:
        raise Exception('مزایده پایان یافته است!')
    if auction.last_bid and user.id == auction.last_bid.user.id:
        raise Exception("شما بالاترین قیمت را در حال حاضر پیشنهاد داده‌اید!")

    if user.bids_number <= 0:
        raise ValueError("مقدار توکن‌های شما کافی نیست!")
    else:
        user.bids_number -= 1
        user.save()

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


def product(request, pk):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('/login/')
        addToCart(pk, request.user)

    product = Product.objects.get(id=pk)

    auctions = Auction.objects.filter(Q(product__id=pk) &
                                      Q(end_time=None))

    context = {'product': product, 'auctions': auctions}

    return render(request, 'base/product.html', context)


def company(request, pk):
    cmp = Company.objects.get(id=pk)

    products = Product.objects.filter(
        Q(company__id=pk)
    )

    auctions = Auction.objects.filter(Q(product__company__id=pk) &
                                      Q(end_time=None))

    context = {'company': cmp, 'products': products, 'auctions': auctions}
    return render(request, 'base/company.html', context)


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

    if request.user.is_authenticated:
        won_auctions = Auction.objects.exclude(end_time=None).filter(last_bid__user=request.user).distinct()
    else:
        won_auctions = None
    context = {'user': user, 'won_auctions': won_auctions, 'owner_user': owner_user, 'deals': deals, 'bids': bids,
               'BID_STEP': BID_STEP}
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


@login_required(login_url='login')
def token(request):
    user = request.user
    errors = []

    if request.method == 'POST':
        number = request.POST.get('number_input')
        if number:
            tokens = int(number)
            if tokens <= 0:
                errors.append('عدد نامعتبر!')
            else:
                user.bids_to_add = tokens
                user.save()
                return buy_token_request(tokens * BID_PRICE)
        return redirect('home')

    context = {'user': user, 'errors': errors}
    return render(request, 'base/token.html', context)


def buy_token_request(amount):
    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": amount,
        "Description": f"{amount} عدد توکن مزایده",
        "CallbackURL": verifyTokenBuyCallbackURL,
    }
    data = json.dumps(data)
    # set content length by data
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
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
def verify_buy_token(request):
    authority = request.GET.get('Authority', '')

    amount = int(request.user.bids_to_add) * BID_PRICE

    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": amount,
        "Authority": authority,
    }
    data = json.dumps(data)
    # set content length by data
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
    response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

    if response.status_code == 200:
        response = response.json()
        if response['Status'] == 100:
            paymentRefID = response["RefID"]

            transaction = Transaction.objects.create(
                payment_number=paymentRefID,
                price=amount
            )

            user = request.user
            user.bids_number += user.bids_to_add
            user.save()

            return render(request, 'base/done-payment.html', {"success": True, "refID": paymentRefID})
        else:
            return render(request, 'base/done-payment.html', {"success": False})
    return HttpResponse(response)
