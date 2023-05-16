import random
from django.utils import timezone
from datetime import datetime, timedelta
from faker import Faker
from django.contrib.auth import get_user_model
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

fake = Faker()
User = get_user_model()
from base.models import User, Company, Product, Auction, Transaction, Deal, Category, DealType, Bid

fake = Faker()


def generate_fake_auctions(num_auctions, *args, **options):
    users = []
    companies = []
    products = []
    auctions = []
    transactions = []
    bids = []
    deals = []
    for _ in range(num_auctions):
        user = User.objects.create(
            id=None,
            username=fake.unique.user_name(),
            name=fake.name(),
            address=fake.address(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
            bids_number=fake.random_int(min=4, max=100)
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
            description=fake.text(),
            category=fake.random_element(elements=[ca.value for ca in Category])
        )
        products.append(product)



        transaction = Transaction.objects.create(
            payment_number=fake.random_number(digits=10),
            price=fake.random_int(min=1, max=1000)
        )
        transactions.append(transaction)

        fake_number = fake.random_int(min=1, max=20)

        for i in range(6):
            deal = Deal.objects.create(
                product=product,
                user=user,
                address=fake.address(),
                transaction=transaction,
                deal_type=fake.random_element(elements=[de.value for de in DealType]),

            )
            deals.append(deal)

        auction = Auction.objects.create(
            product=product,
            start_time=timezone.make_aware(fake.date_time(), timezone.get_current_timezone()),
            current_price=fake.random_int(min=1, max=1000),
            bid_duration=fake.random_int(min=10, max=60),
        )
        auctions.append(auction)

        these_bids = []

        for _ in range(fake_number):
            bid = Bid.objects.create(
                price=fake.random_int(min=1, max=1000),
                auction=auction,
                user=user,
            )
            bids.append(bid)
            these_bids.append(bid)

        sorted_bids = sorted(these_bids, key=lambda bid: bid.created_at)

        newest_bid = sorted_bids[-1] if sorted_bids else None
        auction.last_bid = newest_bid


    for user in users:
        user.save()

    for d in deals:
        d.save()

    for a in auctions:
        a.save()

    users = User.objects.all()
    auctions = Auction.objects.all()

    for i, user in enumerate(users):
        user.bids.set(Bid.objects.filter(user=user))
        user.deals.set(Deal.objects.filter(user=user))

    for i, auction in enumerate(auctions):
        auction.bids.set(Bid.objects.filter(auction=auction))

    Company.objects.bulk_create(companies)
    Product.objects.bulk_create(products)
    Transaction.objects.bulk_create(transactions)
    Bid.objects.bulk_create(bids)


def delete_db():
    Bid.objects.all().delete()
    Product.objects.all().delete()
    Auction.objects.all().delete()
    Transaction.objects.all().delete()
    Deal.objects.all().delete()
    #User.objects.all().delete()
    Company.objects.all().delete()


if __name__ == '__main__':
    #delete_db()

    num_auctions = 60
    generate_fake_auctions(num_auctions)
    # users = User.objects.all()
    # u = random.choice(users) if users else None
    #
    # print(u.bids)
