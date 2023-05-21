import threading
from django.utils import timezone


tasks = dict()

def createNewTaskForAuction(auction):
    print('here')
    try:
        task = tasks[auction.id]
        task.cancel()
    except KeyError:
        pass
    print('and here')

    tasks[auction.id] = threading.Timer(auction.bid_duration, closeAuction, args=(auction, ))


def closeAuction(auction):
    print(auction.id)
    auction.end_time = timezone.now()
    auction.save()
