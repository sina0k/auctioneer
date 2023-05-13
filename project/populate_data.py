import random
from django.utils import timezone
from faker import Faker
from django.contrib.auth import get_user_model
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

fake = Faker()
User = get_user_model()
from base.models import User, Company, Product, Auction, Transaction, Deal

fake = Faker()


def generate_fake_auctions(num_auctions, *args, **options):
    users = []
    companies = []
    products = []
    auctions = []
    transactions = []
    deals = []
    for _ in range(num_auctions):
        user = User.objects.create(
            id=None,
            username=fake.unique.user_name(),
            name=fake.name(),
            address=fake.address(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
            bids=fake.random_int(min=4, max=100)
        )
        users.append(user)

        company = Company.objects.create(
            name=fake.company(),
            description=fake.text()
        )
        companies.append(company)

        product = Product.objects.create(
            company=company,
            name=fake.word(),
            price=fake.random_int(min=10, max=100),
            description=fake.text()
        )
        products.append(product)

        auction = Auction.objects.create(
            product=product,

            start_time=timezone.make_aware(fake.date_time(), timezone.get_current_timezone()),
            current_price=fake.random_int(min=1, max=1000),
            bid_duration=fake.random_int(min=10, max=60),
            last_bidder=user if isinstance(user, User) else None
        )
        auctions.append(auction)

        transaction = Transaction.objects.create(
            payment_number=fake.random_number(digits=10)
        )
        transactions.append(transaction)

        deal = Deal.objects.create(
            product=product,
            buyer=user,
            date_modified=fake.date_time(),
            address=fake.address(),
            deal_type=fake.word(),
            transaction=transaction
        )
        deals.append(deal)

    User.objects.bulk_create(users)
    Company.objects.bulk_create(companies)
    Product.objects.bulk_create(products)
    Auction.objects.bulk_create(auctions)
    Transaction.objects.bulk_create(transactions)
    Deal.objects.bulk_create(deals)


if __name__ == '__main__':
    num_auctions = 50
    generate_fake_auctions(num_auctions)
