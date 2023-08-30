from django.urls import path
from .views import CustomerView, OrderView

urlpatterns = [
    path('customer/', CustomerView.as_view(), name='customer'),
    path('order/', OrderView.as_view(), name='order'),
]
