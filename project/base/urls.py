from django.urls import path
from . import views
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('', views.home, name="home"),
    path('profile/<str:pk>', views.userProfile, name="user-profile"),
    path('update-user', views.updateUser, name="update-user"),
    path('product_list', views.product_list, name="product_list"),
    path('company/<str:pk>/', views.company, name="company"),
    path('auction/<str:pk>/', views.auction, name="auction"),
    path('product/<str:pk>/', views.product, name="product"),
    path('about', views.about, name="about"),
    path('learn', views.learn, name="learn"),
    path('token', views.token, name="token"),

    path('winners', views.winners, name="winners"),
    path('checkout/cart/', views.checkout, name="checkout"),

    path('create-bid/<str:auctionId>', views.createBidHomePage, name="create-bid-home"),

    path('buy-request/', views.send_request, name='request'),
    path('auction-buy-request/<str:pk>', views.auctionPayment, name='pay-auction'),
    path('verify-payment/', views.verify , name='verify'),
    path('verify-auction-payment/<str:pk>/', views.verifyAuctionPayment , name='verify-auction'),
    path('verify-token-payment/', views.verify_buy_token , name='verify-token-buy'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
