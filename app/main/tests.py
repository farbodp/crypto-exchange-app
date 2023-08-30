from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch
from core.models import Customer  # Replace with the actual import
from .common import CRYPTO_PRICE

CREATE_ORDER_URL = reverse('order')

class OrderViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a customer with sufficient balance for testing
        self.customer = Customer.objects.create(name='john', balance=50)
        
    @patch('main.views.OrderStrategyFactory.create_strategy')
    def test_successful_order(self, mock_create_strategy):
        # Mock the strategy instance to avoid actual execution in the test
        mock_strategy = mock_create_strategy.return_value
        mock_strategy.execute.return_value = None

        data = {
            'crypto': 'ABAN',
            'amount': 2,
            'customer_id': self.customer.id,
        }
        initial_balance = self.customer.balance

        response = self.client.post(CREATE_ORDER_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Purchase order registered successfully.'})

        self.customer.refresh_from_db()
        self.assertEqual(
            self.customer.balance,
            initial_balance - Decimal(data['amount'] * CRYPTO_PRICE)
        )

    def test_insufficient_balance(self):
        data = {
            'crypto': 'ABAN',
            'amount': 10,
            'customer_id': self.customer.id,
        }

        response = self.client.post(CREATE_ORDER_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Insufficient account balance.'})
