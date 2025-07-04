from django.core.mail import send_mail

def send_order_email(to_email, name, order_id):
    subject = f"Order #{order_id} Confirmation"
    message = f"Hi {name},\n\nThanks for your order #{order_id}!\nWe'll get it ready by your selected pickup time.\n\n- Your Restaurant"
    
    send_mail(
        subject,
        message,
        None,  # from email (uses DEFAULT_FROM_EMAIL)
        [to_email],
        fail_silently=False
    )
