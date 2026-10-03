from django.urls import path

from .views import OrderCreateView, ProductListView, SendEmailView

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("orders/", OrderCreateView.as_view(), name="order-create"),
    path("send-email/", SendEmailView.as_view(), name="send-email"),
]
