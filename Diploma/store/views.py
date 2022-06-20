import base64
import os

from midi2audio import FluidSynth

import subprocess

from django.shortcuts import render
from django.http import JsonResponse
import json
import uuid

from django.shortcuts import redirect
from django.core.files.base import ContentFile, File
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse

from .models import *
from .templatetags.filters import is_customer
from .utils import cartData, guestOrder, createPaymentInfo, verifyPaymentCallback, confirmOrRefuseHold, print_license

from .forms import CreateCustomerForm, CreateComposerForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


COMPOSER_NET_INCOME_PERCENT = 0.9


def loginPage(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Username or password is incorrect')

    context = {}
    return render(request, 'store/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('/')


def singupPage(request):
    customer_form = CreateCustomerForm()
    composer_form = CreateComposerForm()
    active_form = 'customer'

    if request.method == 'POST':
        if request.POST.get('type') == 'customer':
            form = CreateCustomerForm(request.POST)
            customer_form = form
            active_form = 'customer'
        else:
            form = CreateComposerForm(request.POST)
            composer_form = form
            active_form = 'composer'

        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)

            return redirect('login')

    context = {'active_form': active_form, 'customer_form': customer_form, 'composer_form': composer_form}
    return render(request, 'store/signup.html', context)


def store(request):
    data = cartData(request)
    cartCount = data['cartCount']

    products = Product.objects.all()
    context = {'products': products, 'cartCount': cartCount}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartCount = data['cartCount']

    context = {'items': items, 'order': order, 'cartCount': cartCount}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartCount = data['cartCount']
    personal_data = data['personal_data']

    context = {'items': items, 'order': order, 'cartCount': cartCount, 'personal_data': personal_data}
    return render(request, 'store/checkout.html', context)


def profile(request):
    try:
        client = request.user.customer
        is_composer = False

        data = cartData(request)
        cartCount = data['cartCount']
        personal_data = data['personal_data']
        orderItems = OrderItem.objects.filter(order__complete=True, order__customer=client)

        context = {'order_items': orderItems, 'cartCount': cartCount, 'personal_data': personal_data, 'client': client,
                   'is_composer': is_composer}

    except:
        client = request.user.composer
        is_composer = True

        context = {'client': client, 'is_composer': is_composer}

    return render(request, 'store/profile.html', context)


def product(request):
    try:
        product = Product.objects.get(id=request.GET["id"])
        edit_mode = True
    except:
        product = None
        edit_mode = False

    genres = Genre.objects.all()
    instruments = Instrument.objects.all()
    emotions = Emotion.objects.all()
    try:
        client = request.user.customer
        is_composer = False

    except:
        client = request.user.composer
        is_composer = True

    context = {'client': client, 'is_composer': is_composer, 'genres': genres, 'instruments': instruments,
               'emotions': emotions, 'edit_mode': edit_mode, 'edited_product': product}

    return render(request, 'store/product.html', context)


def my_music(request):
    try:
        client = request.user.customer
        is_composer = False

        data = cartData(request)
        cartCount = data['cartCount']
        items = OrderItem.objects.filter(order__complete=True, order__customer=client)
        composer_orders = ComposerOrder.objects.filter(customer=client, accept=True)

        context = {'items': items, 'cartCount': cartCount, 'client': client,
                   'is_composer': is_composer, 'composer_orders': composer_orders}
    except:
        client = request.user.composer
        products = Product.objects.filter(composer=client)
        composer_orders = ComposerOrder.objects.filter(composer=client, finish=True)
        is_composer = True

        context = {'client': client, 'is_composer': is_composer, 'products': products, 'composer_orders': composer_orders}

    return render(request, 'store/my_music.html', context)


def composers(request):
    data = cartData(request)
    cartCount = data['cartCount']

    composers = Composer.objects.all()
    context = {'composers': composers, 'cartCount': cartCount}

    return render(request, 'store/composers.html', context)


def freelanceList(request):
    freelance_list = FreelanceOrder.objects.all()
    context = {'freelance_list': freelance_list}

    return render(request, 'store/freelance_list.html', context)


def myFreelance(request):
    if is_customer(request.user):
        freelance_list = FreelanceOrder.objects.filter(customer=request.user.customer)

        data = cartData(request)
        cartCount = data['cartCount']
    else:
        freelance_list = FreelanceOrder.objects.filter(bet__composer=request.user.composer)

        cartCount = None

    context = {'freelance_list': freelance_list, 'cartCount': cartCount}

    return render(request, 'store/freelance_list.html', context)


def freelanceOrderInfo(request):
    order = FreelanceOrder.objects.get(id=request.GET["id"])
    try:
        placed_bet = order.bet_set.get(composer=request.user.composer)

        cartCount = None
    except:
        placed_bet = None

        data = cartData(request)
        cartCount = data['cartCount']

    context = {'order': order, 'placed_bet': placed_bet, 'cartCount': cartCount}

    return render(request, 'store/freelance_order_info.html', context)


def myOrders(request):
    try:
        client = request.user.composer
        ordersNew = ComposerOrder.objects.filter(composer=client, finish=False, confirm=None)
        ordersPending = ComposerOrder.objects.filter(composer=client, finish=False, confirm=True,
                                                     customer_confirm=None)
        ordersInWork = ComposerOrder.objects.filter(composer=client, finish=False, confirm=True,
                                                    customer_confirm=True)
        ordersFinished = ComposerOrder.objects.filter(composer=client, finish=True, accept=None)

        cartCount = None
    except:
        client = request.user.customer
        ordersNew = ComposerOrder.objects.filter(customer=client, finish=False, confirm=None)
        ordersPending = ComposerOrder.objects.filter(customer=client, finish=False, confirm=True,
                                                     customer_confirm=None)
        ordersInWork = ComposerOrder.objects.filter(customer=client, finish=False, confirm=True,
                                                    customer_confirm=True)
        ordersFinished = ComposerOrder.objects.filter(customer=client, finish=True, accept=None)

        data = cartData(request)
        cartCount = data['cartCount']

    context = {'orders_new': ordersNew, 'orders_in_work': ordersInWork, 'orders_finished': ordersFinished,
               'orders_pending': ordersPending, 'cartCount': cartCount}

    return render(request, 'store/my_orders.html', context)


def composerOrder(request):
    data = cartData(request)
    cartCount = data['cartCount']

    composer = Composer.objects.get(id=request.GET["id"])
    context = {'composer': composer, 'cartCount': cartCount}

    return render(request, 'store/composer_order.html', context)


def freelanceOrder(request):
    data = cartData(request)
    cartCount = data['cartCount']

    context = { 'cartCount': cartCount }

    return render(request, 'store/freelance_order.html', context)


def aiOrder(request):
    data = cartData(request)
    cartCount = data['cartCount']

    context = { 'cartCount': cartCount, 'genres': Genre.objects.all() }

    return render(request, 'store/ai_order.html', context)


def aiOrderPrepare(request):
    data = json.loads(request.body)

    order, created = AiOrder.objects.update_or_create(
        customer=request.user.customer, completed=False,
        defaults={
            'customer': request.user.customer,
            'genre_id': data['genre_id'],
            'is_premium': data['is_premium'],
            'project': data['project']
        }
    )

    response = {'id': order.id}
    return JsonResponse(response)


def resetAiOrder(request):
    data = json.loads(request.body)
    order = AiOrder.objects.get(id=data['id'])

    order.accepted = False
    order.save()

    return HttpResponse(status=200)


def acceptAiOrder(request):
    data = json.loads(request.body)
    order = AiOrder.objects.get(id=data['id'])
    instrument = Instrument.objects.get(id=data['instrument_id'])

    order.accepted = True
    order.audio_file = File(order.file.path.replace('.mid', '') + '_' + instrument.name + '.mpeg')

    order.save()

    price = 15 if order.is_premium else 5

    payment_info = createPaymentInfo(
        'pay', price, 'AI composition',
        'ai_' + str(order.id),
        "http://185.227.108.95/ai_order_payment_callback/"
    )

    return JsonResponse(payment_info)


@csrf_exempt
def aiOrderPaymentCallback(request):
    data = request.POST.get("data")
    signature = request.POST.get("signature")
    data_object = verifyPaymentCallback(data, signature, "success")

    try:
        order_id = int(data_object["order_id"].replace("ai_", ""))
        order = AiOrder.objects.get(id=order_id)
    except:
        raise Http404()

    if order.completed:
        raise ValidationError("Order is already completed")

    order.completed = True
    order.save()

    return HttpResponse(status=200)


def aiGenerate(request):
    order_id = request.GET['id']
    order = AiOrder.objects.get(id=order_id)

    if not order.accepted:
        guid = str(uuid.uuid4().hex)
        os.makedirs('generated/' + guid)

        command = getPolyphonyCommand(guid=guid)
        proc = subprocess.Popen((command), shell=True)
        proc.wait()

        dir = 'generated/' + guid
        files = os.listdir(dir)

        with open(dir + '/' + files[0], 'rb') as f:
            order.file = File(f)
            order.file.name = guid + '.mid'
            order.save()

    instruments = Instrument.objects.filter(font_path__isnull=False)
    audios = []

    for instrument in instruments:
        fs = FluidSynth(instrument.font_path)
        audio_file = order.file.path.replace('.mid', '') + '_' + instrument.name + '.mpeg'
        fs.midi_to_audio(order.file.path, audio_file)
        file_name = order.file.name.replace('.mid', '') + '_' + instrument.name + '.mpeg'

        audio = {
            'instrument': instrument,
            'file': file_name
        }

        audios.append(audio)

    context = {'order': order, 'audios': audios, 'first_instrument': audios[0]['instrument']}
    return render(request, 'store/ai_generated.html', context)


def getPolyphonyCommand(guid):
    return 'python3 magenta/magenta/models/polyphony_rnn/polyphony_rnn_generate.py \
                --bundle_file=magenta/models/polyphony_rnn.mag \
                --output_dir=generated/' + guid + ' \
                --num_outputs=1 \
                --num_steps=128 \
                --primer_pitches="[67,64,60]" \
                --condition_on_primer=true \
                --inject_primer_during_generation=false'


def getMelodyCommand(guid):
    return 'python3 magenta/magenta/models/melody_rnn/melody_rnn_generate.py \
            --config=attention_rnn \
            --bundle_file=magenta/models/attention_rnn.mag \
            --output_dir=generated/' + guid + ' \
            --num_outputs=1 \
            --num_steps=128 \
            --primer_melody="[60]"'


def betSave(request):
    data = json.loads(request.body)

    order = FreelanceOrder.objects.get(id=data["order_id"])

    bet = Bet(
        text=data["text"],
        price=data["price"],
        composer=request.user.composer,
        freelance_order=order,
    )

    bet.save()

    return HttpResponse(status=200)


def chooseComposer(request):
    data = json.loads(request.body)

    bet = Bet.objects.get(id=data["bet_id"])
    freelance_order = bet.freelance_order

    composer_order = ComposerOrder(
        name=freelance_order.name,
        premium=freelance_order.premium,
        composer=bet.composer,
        customer=request.user.customer,
        description=freelance_order.description,
        price=bet.price,
        confirm=True,
        customer_confirm=None,
        finish=False,
    )

    composer_order.save()
    freelance_order.delete()

    response = {"id": composer_order.id}
    return JsonResponse(response)


def orderComposerConfirm(request):
    data = json.loads(request.body)

    order = ComposerOrder.objects.get(id=data["order_id"])
    order.confirm = data["confirmed"]

    #if order.confirm and order.price == float(data["price"]):
    #    order.customer_confirm = True

    order.price = float(data["price"])
    order.save()

    if not order.confirm:
        order.delete()

    return HttpResponse(status=200)


def orderCustomerConfirm(request):
    data = json.loads(request.body)

    order = ComposerOrder.objects.get(id=data["order_id"])

    if not data["confirmed"]:
        order.delete()

    return HttpResponse(status=200)


def holdPaymentForm(request):
    order = ComposerOrder.objects.get(id=request.GET["id"])
    payment_info = createPaymentInfo(
        'hold',
        order.price,
        "Personal order payment",
        "personal_" + str(order.id),
        "http://185.227.108.95/personal_order_hold_payment_callback/"
    )
    return render(request, 'store/hold_payment_form.html', payment_info)


@csrf_exempt
def personalOrderHoldPaymentCallback(request):
    data = request.POST.get("data")
    signature = request.POST.get("signature")
    data_object = verifyPaymentCallback(data, signature, "hold_wait")

    if data_object["status"] == "success":
        return HttpResponse(status=200)

    try:
        order_id = int(data_object["order_id"].replace("personal_", ""))
        order = ComposerOrder.objects.get(id=order_id)
    except:
        raise Http404()

    if order.customer_confirm:
        raise ValidationError("Order is already confirmed")

    order.customer_confirm = True
    order.save()

    return HttpResponse(status=200)


def sendFile(request):
    data = json.loads(request.body)

    order = ComposerOrder.objects.get(id=data["order_id"])
    order.file = getContentFile(data["file"], order.file)
    order.finish = True

    order.save()

    return HttpResponse(status=200)


def getProductOrdered(request):
    orderId = request.GET["id"]
    accepted = request.GET["accept"] == 'true'
    order = ComposerOrder.objects.get(id=orderId)

    data = cartData(request)
    cartCount = data['cartCount']
    personal_data = data['personal_data']

    context = {'order': order, 'accepted': accepted, 'cartCount': cartCount, 'personal_data': personal_data}
    return render(request, 'store/get_product_ordered.html', context)


def profileSave(request):
    data = json.loads(request.body)

    try:
        client = request.user.customer
    except:
        client = request.user.composer

    client.name = data["profileName"]
    client.email = data["profileEmail"]
    client.save()

    return HttpResponse(status=200)


def acceptOrder(request):
    data = json.loads(request.body)

    order = ComposerOrder.objects.get(id=data["order_id"])

    if data["accepted"]:
        confirmOrRefuseHold("hold_completion", "personal_" + str(order.id))

        order.composer.balance += float(order.price) * COMPOSER_NET_INCOME_PERCENT
        order.composer.save()
    else:
        confirmOrRefuseHold("refund", "personal_" + str(order.id))

    order.accept = data["accepted"]

    if order.accept:
        order.project = data["project"]

        request.user.customer.personaldata.first_name = data["first_name"]
        request.user.customer.personaldata.last_name = data["last_name"]
        request.user.customer.personaldata.country = data["country"]
        request.user.customer.personaldata.city = data["city"]
        request.user.customer.personaldata.phone = data["phone"]
        request.user.customer.personaldata.index = data["index"]
        request.user.customer.personaldata.address = data["address"]
        request.user.customer.personaldata.save()

    order.save()

    feedback = Feedback(
        composer=order.composer,
        order=order,
        mark=float(data["mark"]),
        text=data["text"]
    )

    feedback.save()

    if order.composer.rating is None:
        order.composer.rating = feedback.mark
    else:
        feedback_count = Feedback.objects.filter(composer=order.composer).count()
        order.composer.rating = (order.composer.rating * (feedback_count - 1) + feedback.mark)/feedback_count

    order.composer.save()

    return HttpResponse(status=200)


def personalInfoSave(request):
    data = json.loads(request.body)

    try:
        request.user.customer.personaldata.first_name = data["firstName"]
        request.user.customer.personaldata.last_name = data["lastName"]
        request.user.customer.personaldata.country = data["profileCountry"]
        request.user.customer.personaldata.city = data["profileCity"]
        request.user.customer.personaldata.phone = data["profilePhone"]
        request.user.customer.personaldata.index = data["profileIndex"]
        request.user.customer.personaldata.address = data["profileAddress"]
        request.user.customer.personaldata.save()
    except:
        request.user.composer.first_name = data["firstName"]
        request.user.composer.last_name = data["lastName"]
        request.user.composer.save()

    return HttpResponse(status=200)


def productSave(request):
    data = json.loads(request.body)

    try:
        product = Product.objects.get(id=data["id"])
    except:
        product = Product()
        product.composer = request.user.composer

    product.name = data["name"]
    product.standard_price = data["standard_price"]
    product.premium_price = data["premium_price"]
    product.image = getContentFile(data["image"], product.image)
    product.file = getContentFile(data["file"], product.file)

    product.save()

    product.genres.clear()
    product.instruments.clear()
    product.emotions.clear()

    for genre in data["genres"]:
        product.genres.add(genre)

    for instrument in data["instruments"]:
        product.instruments.add(instrument)

    for emotion in data["emotions"]:
        product.emotions.add(emotion)

    product.save()

    return HttpResponse(status=200)


def orderSave(request):
    data = json.loads(request.body)

    order = ComposerOrder()

    order.composer_id = data["composer_id"]
    order.name = data["name"]
    order.description = data["description"]
    order.premium = data["premium"]
    order.price = data["price"]
    order.customer = request.user.customer
    order.finish = False

    order.save()

    return HttpResponse(status=200)


def freelanceOrderSave(request):
    data = json.loads(request.body)

    order = FreelanceOrder()

    order.name = data["name"]
    order.description = data["description"]
    order.premium = data["premium"]
    order.price = data["price"]
    order.customer = request.user.customer

    order.save()

    return HttpResponse(status=200)


def getContentFile(data, default_value):
    if data == None:
        return default_value

    format, imgstr = data.split(';base64,')
    ext = format.split('/')[-1]
    return ContentFile(base64.b64decode(imgstr), name=str(uuid.uuid4()) + '.' + ext)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action', action)
    print('ProductId', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)

    if action == 'add':
        isPremium = data['is_premium'] == 'true'
        print('IsPremium', isPremium)

        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.update_or_create(
            order=order,
            product=product,
            defaults={'premium': isPremium}
        )
        orderItem.save()
    elif action == 'remove':
        order = Order.objects.get(customer=customer, complete=False)
        orderItem = OrderItem.objects.get(order=order, product=product)
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    order.project = data['project']
    order.save()

    PersonalData.objects.update_or_create(
        customer=customer,
        defaults={
            'first_name': data['shipping']['first_name'],
            'last_name': data['shipping']['last_name'],
            'address': data['shipping']['address'],
            'index': data['shipping']['index'],
            'phone': data['shipping']['phone'],
            'country': data['shipping']['country'],
            'city': data['shipping']['city']
        }
    )

    return getCheckoutInfo(request)


def getCheckoutInfo(request):
    customer = request.user.customer
    order = Order.objects.get(customer=customer, complete=False)
    checkout_info = createPaymentInfo('pay', order.get_cart_total, "Product payment", "product_" + str(order.id), "http://185.227.108.95/checkout_callback/")

    return JsonResponse(checkout_info)


@csrf_exempt
def checkoutCallback(request):
    data = request.POST.get("data")
    signature = request.POST.get("signature")
    data_object = verifyPaymentCallback(data, signature, "success")

    try:
        order_id = int(data_object["order_id"].replace("product_", ""))
        order = Order.objects.get(id=order_id)
    except:
        raise Http404()

    if order.complete:
        raise ValidationError("Order is already completed")

    order.complete = True
    order.transaction_id = data_object["payment_id"]

    for order_item in order.orderitem_set.all():
        price = order_item.product.premium_price if order_item.premium else order_item.product.standard_price
        order_item.product.composer.balance += float(price) * COMPOSER_NET_INCOME_PERCENT
        order_item.product.composer.save()

        licence_file = print_license(
            order_item.product.composer.name,
            order.customer.name,
            order.project,
            order_item.product.name,
            order_item.get_price,
            order.customer.personaldata.country,
            order.customer.personaldata.city,
            order.customer.personaldata.address,
            order.customer.personaldata.index
        )

        with open(licence_file, 'rb') as f:
            order_item.licence_file = File(f)
            order_item.save()

    order.save()

    return HttpResponse(status=200)


@csrf_exempt
def uploadProfileImage(request):
    request.user.customer.image = request.FILES['profile_image']
    request.user.customer.save()


