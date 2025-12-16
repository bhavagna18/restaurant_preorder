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

def send_order_ready_email(to_email, name, order_id):
    subject = f"Your Order #{order_id} is Ready!"
    message = f"Hi {name},\n\nYour order #{order_id} is now ready for pickup.\n\n- Your Restaurant"
    
    send_mail(
        subject,
        message,
        None,
        [to_email],
        fail_silently=False
    )

def send_order_completed_email(to_email, name, order_id):
    subject = f"Your Order #{order_id} is Completed!"
    message = f"Hi {name},\n\nThanks for picking up your order #{order_id}.\nWe hope you enjoy your meal!\n\n- Your Restaurant"
    
    send_mail(
        subject,
        message,
        None,
        [to_email],
        fail_silently=False
    )
