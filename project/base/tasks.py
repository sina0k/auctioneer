import threading
from django.utils import timezone


tasks = dict()

def createNewTaskForAuction(auction):
    try:
        task = tasks[auction.id]
        task.cancel()
    except KeyError:
        pass

    tasks[auction.id] = threading.Timer(auction.bid_duration, closeAuction, args=(auction, ))
    tasks[auction.id].start()


def closeAuction(auction):
    print(auction.id)
    auction.end_time = timezone.now()
    auction.save()
