import json
from django.conf import settings
from twilio.rest import Client
# from twilio.rest import Client
from .utils import send_order_email

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order, OrderItem, MenuItem

# ---------- Public Views ----------

def home(request):
    return render(request, 'orders/home.html')

def menu(request):
    items = MenuItem.objects.all()
    return render(request, 'orders/menu.html', {'menu_items': items})

def cart(request):
    return render(request, 'orders/cart.html')

def send_sms(to_number, name, order_id, ready=False):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    # Correct message based on status
    if ready:
        message = f"Hi {name}, your order #{order_id} is READY for pickup!"
    else:
        message = f"Hi {name}, your order #{order_id} has been successfully placed!"

    client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to='+919848793897'
    )

        


@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        name = request.POST.get('customer_name')
        phone = request.POST.get('phone')
        pickup_time = parse_datetime(request.POST.get('pickup_time'))
        cart_json = request.POST.get('order_data')
        email = request.POST.get('email')

        # ✅ 1. Create the Order
        order = Order.objects.create(
            customer_name=name,
            phone=phone,
            pickup_time=pickup_time,
            status='Pending'
        )

        # ✅ 2. Add Order Items
        try:
            items = json.loads(cart_json)
            for item in items:
                menu_item = MenuItem.objects.get(id=item['id'])
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=item['quantity']
                )
        except Exception as e:
            print("❌ Item saving failed:", e)

        # ✅ 3. Send SMS here
        try:
            send_sms(phone, name, order.id)
        except Exception as e:
            print("❌ SMS failed:", e)


        try:
            send_order_email(email, name, order.id)
        except Exception as e:
            print("❌ Email failed:", e)


        return render(request, 'orders/thank_you.html', {'order': order})

    return render(request, 'orders/checkout.html')


# ---------- Admin Views ----------

@staff_member_required
def order_list(request):
    pending_orders = Order.objects.filter(status='Pending').order_by('-created_at')
    ready_orders = Order.objects.filter(status='Ready').order_by('-created_at')
    completed_orders = Order.objects.filter(status='Completed').order_by('-created_at')

    return render(request, 'orders/order_list.html', {
        'pending_orders': pending_orders,
        'ready_orders': ready_orders,
        'completed_orders': completed_orders,
    })

@csrf_exempt
@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()

        # ✅ Send SMS if marked as READY
        if new_status.upper() == 'READY':
            try:
                send_sms(order.phone, order.customer_name, order.id, ready=True)
            except Exception as e:
                print("❌ SMS (READY) failed:", e)

    return redirect('order_list')
