# Online Shop - Email yuborish funksiyasi (DRF)

## Ishga tushirish
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
python manage.py makemigrations shop
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Mahsulot qo'shish uchun: http://127.0.0.1:8000/admin/

## Endpointlar
| Metod | URL | Vazifasi |
|-------|-----|----------|
| GET | /api/products/ | Mahsulotlar ro'yxati |
| POST | /api/orders/ | Buyurtma yaratish + tasdiqlash emaili |
| POST | /api/send-email/ | Istalgan manzilga email yuborish |

### Misol: /api/send-email/
```json
{"to": "user@mail.com", "subject": "Salom", "message": "Xabar matni"}
```

### Misol: /api/orders/
```json
{
  "customer_name": "Ali",
  "customer_email": "ali@mail.com",
  "address": "Toshkent",
  "items": [{"product": 1, "quantity": 2}]
}
```

## Email sozlash
Default holatda email **terminalga** chiqadi (console backend).
Haqiqiy yuborish uchun `.env` da `EMAIL_BACKEND` ni smtp ga o'zgartiring
va Gmail "App Password" kiriting.

## Testlar
```bash
python manage.py test
```

## Asosiy kod
`shop/emails.py` -> `send_email()` va `send_order_confirmation()`

---

## Signup / Login (accounts ilovasi)

Ishga tushirishdan oldin: `python manage.py makemigrations accounts shop && python manage.py migrate`

### Regex qoidalari (`accounts/validators.py`)
| Maydon | Regex | Qoida |
|--------|-------|-------|
| username | `^[a-zA-Z][a-zA-Z0-9_]{2,19}$` | 3-20 belgi, harf bilan boshlanadi, faqat harf/raqam/_ |
| email | `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$` | nom@domen.tld |
| phone | `^\+998\d{9}$` | +998901234567 (bo'sh joy, tire, qavs avtomatik olib tashlanadi) |
| password | `^(?=.*[A-Za-z])(?=.*\d).{8,}$` | kamida 8 belgi, 1 harf, 1 raqam |

### Endpointlar
| Metod | URL | Vazifasi |
|-------|-----|----------|
| POST | /api/auth/signup/ | Ro'yxatdan o'tish (+ xush kelibsiz emaili), token qaytaradi |
| POST | /api/auth/login/ | Kirish: `login` = username / email / telefon |
| POST | /api/auth/logout/ | Chiqish (`Authorization: Token <token>`) |

```json
// signup
{"username": "ali", "email": "ali@mail.com", "phone": "+998901234567",
 "password": "parol1234", "password2": "parol1234"}

// login (login maydoniga username, email yoki telefon yozish mumkin)
{"login": "ali@mail.com", "password": "parol1234"}
```
