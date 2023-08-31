import time
from django_rq import job


@job
def buy_from_exchange(crypto, amount):
    print('sending purchase request...')
    time.sleep(5)
    print('purchase completed!')
