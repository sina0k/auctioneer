from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from enum import Enum


class DealType(Enum):
    AUCTION = 'Auction'
    BUY = 'Buy'


class Category(Enum):
    ELEC = 'Electronics and Computers'
    CAR = 'Cars'
    BID = 'Bid Packs'
    HOME = "Home, Garden and Tools"
    FASHION = 'Fashion, Health and Beauty'
    CARD = 'Gift Cards'
    KITCHEN = 'Kitchen and Dining'
    OTHER = 'Other'


class Bid(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=0)
    time = models.TimeField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    auction = models.ForeignKey('Auction', on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='bids')


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    address = models.TextField(null=True)
    email = models.EmailField(unique=True, null=True)
    phone = models.CharField(max_length=14, null=True)
    bids_number = models.IntegerField(default=0)
    # User has fields: bids, deals which is defined in those classes with related_name attribute, SO COOL!

    groups = models.ManyToManyField(
        'auth.Group', related_name='custom_user_set', blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='custom_user_set', blank=True
    )


class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()


class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=[(ca.value, ca.name) for ca in Category])


class Auction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    current_price = models.DecimalField(max_digits=10, decimal_places=0)
    bid_duration = models.IntegerField()
    last_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-start_time']


class Transaction(models.Model):
    payment_number = models.CharField(max_length=25)
    price = models.DecimalField(max_digits=10, decimal_places=0, null=False, default=0)


class Deal(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now_add=True)
    address = models.TextField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deals')
    deal_type = models.CharField(max_length=50, choices=[(dt.value, dt.name) for dt in DealType])
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-date_modified']

