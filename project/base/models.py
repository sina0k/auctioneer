from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from enum import Enum
from django.core.validators import MinValueValidator, MaxValueValidator

BID_STEP = 100
BID_PRICE = 800


class DealType(Enum):
    AUCTION = 'Auction'
    BUY = 'Buy'


class Category(Enum):
    ELECT = 'الکترونیک و تکنولوژی'
    CAR = 'ماشین'
    BID = 'توکن پیشنهادها'
    HOME = "وسایل خانه و باغبانی"
    COSMETIC = 'آرایشی بهداشتی'
    FASHION = "پوشاک و فشن"
    CARD = 'کارت هدیه'
    KITCHEN = 'آشپزخانه و غذاخوری'
    FOOD = 'خوراکی و سوپرمارکت'
    OTHER = 'باقی'


class Bid(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    auction = models.ForeignKey('Auction', on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='bids')

    class Meta:
        ordering = ['-created_at']


class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()


class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=[(ca.value, ca.name) for ca in Category])
    image = models.ImageField(upload_to="uploads/products/", null=True, blank=True)


class Discount(models.Model):
    promo_code = models.CharField(max_length=50, blank=True, null=True)
    discount_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    description = models.TextField(null=True, blank=True)


class BuyingProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    cart = models.ForeignKey('ShoppingCart', on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class ShoppingCart(models.Model):
    user = models.OneToOneField('User', null=True, blank=True, on_delete=models.CASCADE, related_name='shopping_cart')


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=14, null=True, blank=True)
    bids_number = models.IntegerField(default=0)
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to="uploads/users/", null=True, blank=True)
    bids_to_add = models.IntegerField(default=0)

    # User has fields: shopping_cart, bids, deals which is defined in those classes with related_name attribute, SO COOL!

    groups = models.ManyToManyField(
        'auth.Group', related_name='custom_user_set', blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='custom_user_set', blank=True
    )


class Auction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=0)
    bid_duration = models.IntegerField()
    last_bid = models.ForeignKey(Bid, on_delete=models.SET_NULL, null=True, blank=True, related_name="auction_last_bid")
    has_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_time']


class Transaction(models.Model):
    payment_number = models.CharField(max_length=25)
    price = models.DecimalField(max_digits=10, decimal_places=0, null=False, default=0)


class Deal(models.Model):
    cart = models.OneToOneField('ShoppingCart', on_delete=models.CASCADE, related_name='deal')
    date_modified = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deals')
    deal_type = models.CharField(max_length=50, choices=[(dt.value, dt.name) for dt in DealType])
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals')

    class Meta:
        ordering = ['-date_modified']
