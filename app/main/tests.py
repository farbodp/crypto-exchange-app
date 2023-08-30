from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch
from core.models import Customer  # Replace with the actual import

class OrderViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a customer with sufficient balance for testing
        self.customer = Customer.objects.create(name='john', balance=10)

    def test_insufficient_balance(self):
        url = reverse('order')  # Replace 'order-view' with your actual URL name
        data = {
            'crypto': 'ABAN',
            'amount': 10,
            'customer_id': self.customer.id,
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Insufficient account balance.'})
