from abc import ABC, abstractmethod
from core.models import Customer, AbanWallet, Order
from django.db import models

from .tasks import buy_from_exchange
from .common import PURCHASE_THRESHOLD, CRYPTO_PRICE


class OrderStrategy(ABC):
    @abstractmethod
    def execute(self, request, customer, crypto, amount, total_price):
        pass


class SmallOrderStrategy(OrderStrategy):
    def execute(self, request, customer, crypto, amount, total_price):
        pending_orders = Order.objects.filter(status='pending')
        pending_total = pending_orders.aggregate(
            total_price=models.Sum('price')
        )['total_price']

        if pending_total is None:
            pending_total = 0

        pending_total += total_price

        if pending_total >= PURCHASE_THRESHOLD:
            buy_from_exchange.delay(crypto, pending_total)
            pending_orders.update(status='completed')
            Order.objects.create(
                price=total_price,
                quantity=amount,
                status='completed',
                customer_id=customer.id,
            )
        else:
            Order.objects.create(
                price=total_price,
                quantity=amount,
                status='pending',
                customer_id=customer.id,
            )


class LargeOrderStrategy(OrderStrategy):
    def execute(self, request, customer, crypto, amount, total_price):
        buy_from_exchange.delay(crypto, amount)
        Order.objects.create(
            price=total_price,
            quantity=amount,
            status='completed',
            customer_id=customer.id,
        )


class OrderStrategyFactory:
    @staticmethod
    def create_strategy(total_price):
        if total_price < PURCHASE_THRESHOLD:
            return SmallOrderStrategy()
        else:
            return LargeOrderStrategy()
