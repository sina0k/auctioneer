from django.contrib import admin

from .models import Company, Product, Auction, Transaction, Deal, User, Bid, Discount

admin.site.register(Company)
admin.site.register(Product)
admin.site.register(Auction)
admin.site.register(Transaction)
admin.site.register(Deal)
admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Discount)

# Register your models here.
