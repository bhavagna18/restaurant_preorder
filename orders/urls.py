from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart, name='cart'),

    # Staff-only views
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
]
