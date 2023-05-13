from django.contrib import admin

from .models import Company, Product, Auction, Transaction, Deal, User

admin.site.register(Company)
admin.site.register(Product)
admin.site.register(Auction)
admin.site.register(Transaction)
admin.site.register(Deal)
admin.site.register(User)

# Register your models here.
