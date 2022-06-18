import json

import requests

from .models import *

import hashlib
import base64

from django.core.exceptions import PermissionDenied, ValidationError

PUBLIC_KEY = 'sandbox_i82775220823'
PRIVATE_KEY = 'sandbox_QGD2tObrPtiOZrbtebzRTRhH8TAFD0f1uhPp3ey2'
SHA1 = hashlib.sha1()

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('Cart:', cart)
    items = []
    order = {'get_cart_total': 0, 'get_cart_count': len(cart)}
    cartCount = order['get_cart_count']

    for i in cart:
        try:
            is_premium = cart[i]['is_premium'] == "true"

            product = Product.objects.get(id=i)
            price = product.premium_price if is_premium else product.standard_price

            order['get_cart_total'] += price
            order_item = {
                'premium': is_premium,
                'product': {
                    'id': product.id,
                    'image_url': product.image_url,
                    'name': product.name,
                    'premium_price': product.premium_price,
                    'standard_price': product.standard_price,
                    'composer': product.composer
                }
            }
            items.append(order_item)
        except:
            pass

    return {'items': items, 'order': order, 'cartCount': cartCount}


def cartData(request):
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
            personal_data = request.user.customer.get_personal_data
            cartCount = order.get_cart_count
        except:
            order = None
            items = None
            personal_data = None
            cartCount = 0
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartCount = cookieData['cartCount']
        personal_data = None
    return {'items': items, 'order': order, 'cartCount': cartCount, 'personal_data': personal_data}


def guestOrder(request, data):
    print('User is not logged in')

    print('COOKIES', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email=email,
        defaults={
            'name': name,
            'email': email
        }
    )

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
        )
    return order, customer


def getSignature(data_base64):
    signature = PRIVATE_KEY + data_base64 + PRIVATE_KEY
    signature = hashlib.sha1(bytes(signature, 'utf-8')).digest()
    return str(base64.b64encode(signature), 'utf-8')


def createPaymentInfo(action, price, description, order_id, callback_url):
    payment_info = {
        "public_key": PUBLIC_KEY,
        "action": action,
        "amount": str(price),
        "currency": "USD",
        "description": description,
        "order_id": order_id,
        "server_url": callback_url,
        "version": "3"
    }

    payment_info_json = json.dumps(payment_info)
    payment_info_base64 = str(base64.b64encode(bytes(payment_info_json, 'utf-8')), 'utf-8')

    signature = getSignature(payment_info_base64)

    return {
        "data": payment_info_base64,
        "signature": signature
    }


def confirmOrRefuseHold(action, order_id):
    hold_confirm_info = {
        'action': action,
        'version': 3,
        'public_key': PUBLIC_KEY,
        'order_id': order_id
    }
    hold_confirm_info_json = json.dumps(hold_confirm_info)

    hold_confirm_info_base64 = str(base64.b64encode(bytes(hold_confirm_info_json, 'utf-8')), 'utf-8')
    signature = getSignature(hold_confirm_info_base64)

    confirmation = {
        'data': hold_confirm_info_base64,
        'signature': signature
    }

    requests.post('https://www.liqpay.ua/api/request', confirmation)


def verifyPaymentCallback(data, signature, alt_success_status):
    actualSignature = getSignature(data)

    if actualSignature != signature:
        raise PermissionDenied()

    data_json = str(base64.b64decode(bytes(data, 'utf-8')), 'utf-8')
    data_object = json.loads(data_json)

    print(data_object)

    if data_object["status"] != "success" and data_object["status"] != alt_success_status:
        raise ValidationError("Non successful operation")

    return data_object


