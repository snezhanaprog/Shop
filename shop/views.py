from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
import json
from account.urls import *
from django.core.files.storage import FileSystemStorage
from .forms import CommentForm
from django.contrib import messages

def get_product_filter_min(mas):
    n = len(mas)
    products = list(mas)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if products[j].price > products[j + 1].price:
                products[j], products[j + 1] = products[j + 1], products[j]
    return products


def get_product_filter_max(mas):
    n = len(mas)
    products = list(mas)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if products[j].price < products[j + 1].price:
                products[j], products[j + 1] = products[j + 1], products[j]
    return products

def cart(request):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        order_products = order.orderproduct_set.all()
        count_orderproducts = order.get_cart_total_quantity
        count = order.get_cart_total - order.get_cart_total / 100 * 5
    else:
        order_products = []
        order = {
            'get_cart_total': 0,
            'get_cart_products': 0,
        }
        count_orderproducts = 0
        count = 0
    context = {
        'order_products': order_products,
        'count_orderproducts': count_orderproducts,
        'order': order,
        'count': count,
        'user': request.user,
    }

    return render(request, 'cart.html', context)

def store(request):
    products = Product.objects.all()
    order_products = []
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        order_products = order.get_products
    if 'filter_min' in request.POST:
        products = get_product_filter_min(products)
    elif 'filter_max' in request.POST:
        products = get_product_filter_max(products)
    elif 'search' in request.POST:
        search_value = request.POST.get('search_value')
        products = products.filter(name__icontains=search_value)
    context = {
        'products': products,
        'order_products': order_products,
        'user': request.user,
    }
    return render(request, 'store.html', context)


def face_page(request):
    context = {'user': request.user}
    return render(request, 'face-page.html',context)

def about(request):
    context = {'user': request.user}
    return render(request, 'about.html', context)

def feedback(request):
    context = {'user': request.user}
    return render(request, 'feedback.html', context)

def contacts(request):
    context = {'user': request.user}
    return render(request, 'contacts.html', context)
def achievements(request):
    context = {
        'achievements': Achievement.objects.filter(user=request.user),
        'user': request.user
    }
    return render(request, 'achievements.html', context)

def checkout(request):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        products = order.orderproduct_set.all()
    else:
        products = []
        order = {
            'get_cart_total': 0,
            'get_cart_products': 0
        }
    context = {
        'products': products,
        'order': order,
        'user': request.user
    }
    return render(request, 'checkout.html', context)

def add_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    user = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(user=user, complete=False)
    orderProduct, created = OrderProduct.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderProduct.quantity += 1
    elif action == 'remove':
        orderProduct.quantity -= 1

    orderProduct.save()

    if orderProduct.quantity <= 0:
        orderProduct.delete()
    elif action == 'remove-all':
        orderProduct.delete()

    return JsonResponse("Item update", safe=False)


def product_details(request, id):
    product = Product.objects.get(id=id)
    comments = Comment.objects.filter(product=product)
    if request.user.is_authenticated:
        if request.method == 'POST':
            user = request.user
            product = Product.objects.get(id=id)
            order, created = Order.objects.get_or_create(user=user, complete=False)
            orderProduct, created = OrderProduct.objects.get_or_create(order=order, product=product)
            orderProduct.quantity += 1
            orderProduct.save()
        action, created = Action.objects.get_or_create(user=request.user)
        if (action.count_details_view == 0):
            achie = Achievement.objects.create(
                title="Молодец, заинтересовался",
                description="Получено за первый просмотр подробного описания товара ",
                user=request.user
            )
            messages.success(request, "Молодец, заинтересовался")
        elif (action.count_details_view == 9):
            achie = Achievement.objects.create(
                title="Начинающий следопыт",
                description="Получено за 10-ый просмотр подробного описания товара",
                user=request.user
            )
            messages.success(request, "Начинающий следопыт")
        elif (action.count_details_view == 25):
            achie = Achievement.objects.create(
                title="Вот это ты любопытный)",
                description="Получено за 25-ый просмотр подробного описания товара",
                user=request.user
            )
            messages.success(request, "Вот это ты любопытный)")
        action.count_details_view += 1
        action.save()
    context = {
        'product': product,
        'comments': comments,
        'user': request.user,
    }
    return render(request, 'details.html', context)

def comments(request,id):
    product = Product.objects.get(id=id)
    comments = Comment.objects.filter(product=product)
    #images = [i.image for i in comments]
    context = {
        'product': product,
        'comments': comments,
        'user': request.user,
        #'images': images,
    }

    return render(request, 'comments.html', context)

def create_comment(request,id):
    product = Product.objects.get(id=id)
    if request.user.is_authenticated:
        if(request.method == "POST"):
            body = request.POST.get('comment-body')
            image = []
            if request.FILES:
                image = request.FILES.get('image')
            comment = Comment.objects.create(
                product=product,
                body=body,
                user=request.user,
                image=image
            )
            action, created = Action.objects.get_or_create(user=request.user)
            if (action.count_comments_all == 0):
                achie = Achievement.objects.create(
                    title="Юный критик",
                    description="Получено за написание своего первого отзыва к товару",
                    user=request.user
                )
                messages.success(request, "Юный критик")
            elif (action.count_comments_all == 9):
                achie = Achievement.objects.create(
                    title="Критик с опытом",
                    description="Получено за написание 10 отзывов",
                    user=request.user
                )
                messages.success(request, "Критик с опытом")
            action.count_comments_all += 1
            action.save()
            return redirect('product_details', id=id)
    context = {
        'product': product,
        'user': request.user
    }
    return render(request, 'create-comment.html', context)
