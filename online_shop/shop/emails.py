"""
Email yuborish funksiyalari.

send_email()              - umumiy funksiya (istalgan joydan chaqiriladi)
send_order_confirmation() - buyurtma tasdiqlash xabari
"""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def send_email(subject, message, recipient_list, html_message=None):
    """
    Email yuboradi.

    :param subject: xat mavzusi
    :param message: oddiy matn
    :param recipient_list: qabul qiluvchilar ro'yxati, masalan ["a@mail.com"]
    :param html_message: ixtiyoriy HTML ko'rinish
    :return: muvaffaqiyatli bo'lsa True, aks holda False
    """
    if isinstance(recipient_list, str):
        recipient_list = [recipient_list]

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
        )
        if html_message:
            email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception:
        # Email xatosi butun so'rovni buzmasligi uchun logga yozamiz
        logger.exception("Email yuborishda xatolik: %s", recipient_list)
        return False


def send_order_confirmation(order):
    """Buyurtma yaratilgandan keyin mijozga tasdiqlash xati yuboradi."""
    lines = []
    rows = ""
    for item in order.items.select_related("product"):
        lines.append(
            f"- {item.product.name} x {item.quantity} = {item.subtotal} so'm"
        )
        rows += (
            f"<tr><td>{item.product.name}</td><td>{item.quantity}</td>"
            f"<td>{item.subtotal} so'm</td></tr>"
        )

    subject = f"Buyurtmangiz qabul qilindi (#{order.pk})"
    message = (
        f"Assalomu alaykum, {order.customer_name}!\n\n"
        f"Buyurtmangiz #{order.pk} qabul qilindi.\n\n"
        + "\n".join(lines)
        + f"\n\nJami: {order.total_price} so'm\n\n"
        "Xaridingiz uchun rahmat!"
    )
    html_message = f"""
    <h2>Assalomu alaykum, {order.customer_name}!</h2>
    <p>Buyurtmangiz <b>#{order.pk}</b> qabul qilindi.</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><th>Mahsulot</th><th>Soni</th><th>Narxi</th></tr>
      {rows}
    </table>
    <p><b>Jami: {order.total_price} so'm</b></p>
    <p>Xaridingiz uchun rahmat!</p>
    """
    return send_email(subject, message, [order.customer_email], html_message)
