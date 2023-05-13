from django.contrib import admin

from .models import Company, Product, Auction, Transaction, Deal

admin.site.register(Company)
admin.site.register(Product)
admin.site.register(Auction)
admin.site.register(Transaction)
admin.site.register(Deal)



# Register your models here.
