import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseBadRequest
from .models import Order, OrderItem, MenuItem
from .utils import send_order_email, send_order_ready_email, send_order_completed_email


def home(request):
    return render(request, 'orders/home.html')


def menu(request):
    items = MenuItem.objects.all()
    return render(request, 'orders/menu.html', {'menu_items': items})


def cart(request):
    return render(request, 'orders/cart.html')

@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        name = request.POST.get('customer_name')
        phone = request.POST.get('phone')
        pickup_time = parse_datetime(request.POST.get('pickup_time'))
        cart_json = request.POST.get('order_data')
        email = request.POST.get('email')

        if not all([name, phone, pickup_time, cart_json, email]):
            return HttpResponseBadRequest("Missing required fields.")

        order = Order.objects.create(
            customer_name=name,
            phone=phone,
            email=email,
            pickup_time=pickup_time,
            status='Pending'
        )

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
            return HttpResponseBadRequest("Invalid cart data.")

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
        if new_status:
            order.status = new_status
            order.save()

            # Send email based on status
            if new_status == 'Ready':
                send_order_ready_email(order.email, order.customer_name, order.id)
            elif new_status == 'Completed':
                send_order_completed_email(order.email, order.customer_name, order.id)

    return redirect('order_list')