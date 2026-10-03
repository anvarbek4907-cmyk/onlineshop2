from django.core import mail
from django.test import override_settings
from rest_framework.test import APITestCase

from .models import Product


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EmailTests(APITestCase):
    def test_send_email_endpoint(self):
        r = self.client.post(
            "/api/send-email/",
            {"to": "test@mail.com", "subject": "Salom", "message": "Test"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Salom")

    def test_order_sends_confirmation(self):
        p = Product.objects.create(name="Telefon", price=1000, stock=5)
        r = self.client.post(
            "/api/orders/",
            {
                "customer_name": "Ali",
                "customer_email": "ali@mail.com",
                "items": [{"product": p.id, "quantity": 2}],
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertTrue(r.data["email_sent"])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ali@mail.com"])
