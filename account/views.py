from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .forms import UserRegisterForm
from shop.urls import *

def is_upper_in_word(word:str):
        for a in word:
            if a == a.upper():
                return True
        return False


def is_lower_in_word(word: str):
    for a in word:
        if a == a.lower():
            return True
    return False


def is_symbol_in_word(word):
    for a in word:
        if a == a.digit():
            return True
    return False

def authorization(request):
    message: str = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(username, password)
        if user is not None:
            login(request, user)
            return redirect('face-page')
        else:
            message = "Неправильный логин или пароль"
    context = {
        'message': message,
    }
    return render(request, 'authorization.html', context)

def log_out(request):
    logout(request)
    return redirect('authorization')
def registration(request):
    message: str = None
    form = UserRegisterForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if User.objects.filter(email=request.POST.get('email'), is_active=True).exists():
            message = "Эта почта уже зарегистрирована"
        elif len(request.POST.get('password1')) < 8:
            message = "Пароль должен содержать не менее 8 символов"
        elif request.POST.get('password1').isdigit():
            message = "Пароль не может быть полностью числовым"
        elif request.POST.get('password1') != request.POST.get('password2'):
            message = "Пароли не совпадают"
        elif form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Ссылка для активации была отправлена на ваш электронный адрес'
            message = render_to_string('message_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render(request, 'confirmation.html')
        else:
            message = "Ваш пароль не может быть широко используемым паролем"

    context = {
        'form': form,
        'message': message,
    }
    return render(request, 'registration.html', context)

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'confirmComplete.html')
    else:
        return render(request, 'notConfirm.html')

