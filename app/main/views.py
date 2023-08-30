from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Customer, AbanWallet, Order
from .serializers import CustomerSerializer, AbanWalletSerializer, OrderSerializer
from decimal import Decimal
import time
from django.db import models

from .tasks import buy_from_exchange
from .common import CRYPTO_PRICE, PURCHASE_THRESHOLD
from .utils import OrderStrategyFactory
from django.db import transaction


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
        customer = Customer.objects.get(id=customer_id)
        total_price = Decimal(amount * CRYPTO_PRICE)

        if customer.balance < total_price:
            return Response({'error': 'Insufficient account balance.'}, status=400)

        customer.balance -= total_price
        customer.save()

        order_strategy = OrderStrategyFactory.create_strategy(total_price)
        order_strategy.execute(request, customer, crypto, amount, total_price)

        return Response({'message': 'Purchase order registered successfully.'})






