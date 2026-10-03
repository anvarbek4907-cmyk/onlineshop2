from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .emails import send_email, send_order_confirmation
from .models import Order, Product
from .serializers import OrderSerializer, ProductSerializer, SendEmailSerializer


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderCreateView(generics.CreateAPIView):
    """Buyurtma yaratadi va mijozga tasdiqlash emailini yuboradi."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        email_sent = send_order_confirmation(order)

        data = self.get_serializer(order).data
        data["email_sent"] = email_sent
        return Response(data, status=status.HTTP_201_CREATED)


class SendEmailView(APIView):
    """Berilgan manzilga istalgan xabarni yuboradi."""

    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        ok = send_email(d["subject"], d["message"], [d["to"]])
        if ok:
            return Response({"detail": "Email yuborildi."})
        return Response(
            {"detail": "Email yuborishda xatolik yuz berdi."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
