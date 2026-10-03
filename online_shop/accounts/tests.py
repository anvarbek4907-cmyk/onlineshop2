from django.core import mail
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APITestCase

from . import validators as v
from django.core.exceptions import ValidationError


class RegexTests(SimpleTestCase):
    def test_username(self):
        for ok in ["ali", "Ali_123", "a_b"]:
            self.assertTrue(v.USERNAME_REGEX.match(ok), ok)
        for bad in ["a", "1ali", "ali baliyev", "ali!", "a" * 21]:
            self.assertFalse(v.USERNAME_REGEX.match(bad), bad)

    def test_email(self):
        for ok in ["ali@mail.com", "a.b+c@sub.domain.uz"]:
            self.assertTrue(v.EMAIL_REGEX.match(ok), ok)
        for bad in ["ali@", "@mail.com", "ali@mail", "ali mail@x.com"]:
            self.assertFalse(v.EMAIL_REGEX.match(bad), bad)

    def test_phone(self):
        self.assertEqual(v.validate_phone("+998 (90) 123-45-67"), "+998901234567")
        for bad in ["901234567", "+99890123456", "+9989012345678", "+998abc"]:
            with self.assertRaises(ValidationError):
                v.validate_phone(bad)

    def test_password(self):
        self.assertTrue(v.PASSWORD_REGEX.match("abc12345"))
        for bad in ["abcdefgh", "12345678", "ab12"]:
            self.assertFalse(v.PASSWORD_REGEX.match(bad), bad)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AuthTests(APITestCase):
    data = {
        "username": "ali",
        "email": "ali@mail.com",
        "phone": "+998901234567",
        "password": "parol1234",
        "password2": "parol1234",
    }

    def signup(self, **extra):
        return self.client.post("/api/auth/signup/", {**self.data, **extra}, format="json")

    def test_signup_ok_and_welcome_email(self):
        r = self.signup()
        self.assertEqual(r.status_code, 201)
        self.assertIn("token", r.data)
        self.assertEqual(len(mail.outbox), 1)

    def test_signup_invalid_fields(self):
        self.assertEqual(self.signup(username="1ali").status_code, 400)
        self.assertEqual(self.signup(email="bad@").status_code, 400)
        self.assertEqual(self.signup(phone="123").status_code, 400)
        self.assertEqual(self.signup(password="short", password2="short").status_code, 400)
        self.assertEqual(self.signup(password2="boshqa1234").status_code, 400)

    def test_signup_duplicates(self):
        self.signup()
        self.assertEqual(self.signup().status_code, 400)

    def test_login_by_username_email_phone(self):
        self.signup()
        for login in ["ali", "ali@mail.com", "+998901234567"]:
            r = self.client.post(
                "/api/auth/login/", {"login": login, "password": "parol1234"}, format="json"
            )
            self.assertEqual(r.status_code, 200, login)
            self.assertIn("token", r.data)

    def test_login_wrong_password_and_format(self):
        self.signup()
        r = self.client.post("/api/auth/login/", {"login": "ali", "password": "xato"}, format="json")
        self.assertEqual(r.status_code, 400)
        r = self.client.post("/api/auth/login/", {"login": "!!", "password": "x"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_logout(self):
        token = self.signup().data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(self.client.post("/api/auth/logout/").status_code, 200)
