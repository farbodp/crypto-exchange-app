from rest_framework import serializers
from core.models import Customer, AbanWallet, Order


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class AbanWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbanWallet
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
