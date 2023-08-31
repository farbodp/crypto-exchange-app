"""
Database models.
"""

from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    name = models.CharField(max_length=20)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=100.00
    )


class AbanWallet(models.Model):
    balance = models.DecimalField(
        max_digits=20, decimal_places=10, default=0.0
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity = models.DecimalField(
        max_digits=20, decimal_places=10, default=0.0
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
        ],
        default='pending',
    )
