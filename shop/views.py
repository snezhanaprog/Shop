from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from .models import *
from .utils import UserContextMixin
import json
from django.contrib import messages


class CartView(View):
    template_name = 'cart.html'

    def get(self, request, *args, **kwargs):
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
        return render(request, self.template_name, context)


class StoreView(View):
    template_name = 'store.html'

    def get_order_products(self, user):
        if user.is_authenticated:
            order, created = Order.objects.get_or_create(user=user, complete=False)
            return order.get_products
        return []

    def get_context_data(self, request, products, order_products):
        return {
            'products': products,
            'order_products': order_products,
            'user': request.user,
        }

    def get_products(self, request):
        products = Product.objects.all()
        filter_option = request.POST.get('filter')
        if filter_option == 'min':
            products = products.order_by('price')
        elif filter_option == 'max':
            products = products.order_by('-price')
        elif 'search' in request.POST:
            search_value = request.POST.get('search_value')
            products = products.filter(name__icontains=search_value)
        return products

    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        order_products = self.get_order_products(request.user)
        context = self.get_context_data(request, products, order_products)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        products = self.get_products(request)
        order_products = self.get_order_products(request.user)
        context = self.get_context_data(request, products, order_products)
        return render(request, self.template_name, context)


class FacePageView(UserContextMixin, TemplateView):
    template_name = 'face-page.html'


class AboutView(UserContextMixin, TemplateView):
    template_name = 'about.html'


class FeedbackView(UserContextMixin, TemplateView):
    template_name = 'feedback.html'


class ContactsView(UserContextMixin, TemplateView):
    template_name = 'contacts.html'


class Achievements(ListView):
    model = Achievement
    context_object_name = 'achievements'
    template_name = 'achievements.html'

    def get_queryset(self):
        return Achievement.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class Checkout(View):
    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            order, created = Order.objects.get_or_create(user=request.user, complete=False)
            products = order.orderproduct_set.all()
        else:
            products = []
            order = {'get_cart_total': 0, 'get_cart_products': 0}

        context = {
            'products': products,
            'order': order,
            'user': request.user
        }
        return render(request, self.template_name, context)


def add_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    orderProduct, created = OrderProduct.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderProduct.quantity += 1
    elif action == 'remove':
        orderProduct.quantity -= 1

    orderProduct.save()

    if orderProduct.quantity <= 0 or action == 'remove-all':
        orderProduct.delete()

    return JsonResponse("Товар добавлен", safe=False)


class ProductDetail(View):
    template_name = 'details.html'

    def get_object(self, id):
        return get_object_or_404(Product, id=id)

    def get(self, request, id, *args, **kwargs):
        product = self.get_object(id)
        comments = Comment.objects.filter(product=product)
        context = {
            'product': product,
            'comments': comments,
            'user': request.user,
        }
        return render(request, self.template_name, context)

    def post(self, request, id, *args, **kwargs):
        product = self.get_object(id)
        order, created = Order.objects.get_or_create(user=request.user, complete=False)
        orderProduct, created = OrderProduct.objects.get_or_create(order=order, product=product)
        orderProduct.quantity += 1
        orderProduct.save()
        self.handle_achievements(request.user)
        return self.get(request, id)

    def handle_achievements(self, user):
        action, created = Action.objects.get_or_create(user=user)
        achievements = {
            0: ("Молодец, заинтересовался", "Получено за первый просмотр подробного описания товара "),
            9: ("Начинающий следопыт", "Получено за 10-ый просмотр подробного описания товара"),
            25: ("Вот это ты любопытный)", "Получено за 25-ый просмотр подробного описания товара"),
        }
        if action.count_details_view in achievements:
            title, description = achievements[action.count_details_view]
            achie = Achievement.objects.create(
                title=title,
                description=description,
                user=user
            )
        action.count_details_view += 1
        action.save()


class ProductCommentsView(DetailView):
    model = Product
    template_name = 'comments.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        comments = product.comment_set.all()
        context['comments'] = comments
        context['user'] = self.request.user
        return context


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


class CreateCommentView(View):
    template_name = 'create-comment.html'

    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)
        context = {'product': product, 'user': request.user}
        return render(request, self.template_name, context)

    def post(self, request, id):
        product = get_object_or_404(Product, pk=id)
        if request.user.is_authenticated:
            body = request.POST.get('comment-body')
            image = request.FILES.get('image') if 'image' in request.FILES else None
            comment = Comment.objects.create(
                product=product,
                body=body,
                user=request.user,
                image=image
            )
            action, created = Action.objects.get_or_create(user=request.user)
            if action.count_comments_all == 0:
                achie = Achievement.objects.create(
                    title="Юный критик",
                    description="Получено за написание своего первого отзыва к товару",
                    user=request.user
                )
            elif action.count_comments_all == 9:
                achie = Achievement.objects.create(
                    title="Критик с опытом",
                    description="Получено за написание 10 отзывов",
                    user=request.user
                )
            action.count_comments_all += 1
            action.save()
            return redirect('product_details', id=id)
        return self.get(request, id)