from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Customer, AbanWallet, Order
from .serializers import CustomerSerializer, AbanWalletSerializer, OrderSerializer
from decimal import Decimal
import time
from django.db import models

from .tasks import buy_from_exchange
from django.db import transaction


class OrderStrategy:
    def execute(self, request, customer, crypto, amount, total_price):
        pass


class SmallOrderStrategy(OrderStrategy):
    def execute(self, request, customer, crypto, amount, total_price):
        pending_orders = Order.objects.filter(status='pending')
        pending_total = pending_orders.aggregate(total_price=models.Sum('price'))['total_price']

        if pending_total is None:
            pending_total = 0

        pending_total += total_price

        if pending_total >= 10:
            buy_from_exchange.delay(crypto, pending_total)
            ###TODO: PUT below two line inside above
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
        if total_price < 10:
            return SmallOrderStrategy()
        else:
            return LargeOrderStrategy()


class CustomerView(APIView):
    def get(self, request, format=None):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderView(APIView):

    @transaction.atomic
    def post(self, request, format=None):
        crypto = request.data.get('crypto')
        amount = request.data.get('amount')
        customer_id = request.data.get('customer_id')
        price = 10  # Replace with actual logic to fetch cryptocurrency price
        customer = Customer.objects.get(id=customer_id)
        total_price = Decimal(amount * price)

        if customer.balance < total_price:
            return Response({'error': 'Insufficient account balance.'}, status=400)

        customer.balance -= total_price
        customer.save()

        strategy = OrderStrategyFactory.create_strategy(total_price)
        strategy.execute(request, customer, crypto, amount, total_price)

        return Response({'message': 'Purchase order registered successfully.'})






