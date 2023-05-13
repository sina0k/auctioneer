from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    address = models.TextField(null=True)
    email = models.EmailField(unique=True, null=True)
    phone = models.CharField(max_length=14, null=True)
    bids = models.IntegerField()

    # Add the related_name arguments to resolve the clashes
    groups = models.ManyToManyField(
        'auth.Group', related_name='custom_user_set', blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='custom_user_set', blank=True
    )


# phone = PhoneNumberField()


class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()


class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    description = models.TextField()


class Auction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    current_price = models.DecimalField(max_digits=10, decimal_places=0)
    bid_duration = models.IntegerField()
    last_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-start_time']


class Transaction(models.Model):
    payment_number = models.CharField(max_length=25)


class Deal(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now_add=True)
    address = models.TextField(null=False)
    deal_type = models.CharField(max_length=10)  # Updated field name
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True)
