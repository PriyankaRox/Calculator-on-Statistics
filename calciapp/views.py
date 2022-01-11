from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.views import View
from .utils import Util
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
import statistics
from .forms import CreateUserForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .helpers import send_forget_password_mail
import uuid
from django.contrib import auth

# Create your views here.


def login(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('index')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


def forgotpassword(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        form = CreateUserForm()
        try:
            if request.method == 'POST':
                username = request.POST.get('username')
                if not form.objects.filter(username=username).first():
                    messages.success(request, 'Not user found with this username.')
                    return redirect('/forgotpassword/')
                user_obj = form.objects.get(username=username)
                token = str(uuid.uuid4())
                profile_obj = form.objects.get(user=user_obj)
                profile_obj.forget_password_token = token
                profile_obj.save()
                send_forget_password_mail(user_obj.email, token)
                messages.success(request, 'An email is sent.')
                return redirect('/forget-password/')
        except Exception as e:
            print(e)
        return render(request, 'forgotpassword.html')


def ChangePassword(request, token):
    context = {}
    form = CreateUserForm()
    try:
        profile_obj = form.objects.filter(forget_password_token=token).first()
        context = {'user_id': profile_obj.user.id}

        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')

            if user_id is None:
                messages.success(request, 'No user id found.')
                return redirect(f'/change-password/{token}/')

            if new_password != confirm_password:
                messages.success(request, 'both should  be equal.')
                return redirect(f'/change-password/{token}/')

            user_obj = form.objects.get(id=user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return redirect('/login/')
    except Exception as e:
        print(e)
    return render(request, 'change-password.html', context)



@csrf_exempt
def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        form = CreateUserForm()
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('email')
                #user = form.objects.get(email=form['email'])
                #token = RefreshToken.for_user(user).access_token
                current_site = get_current_site(request).domain
                relativeLink = reverse('email-verify')
                #absurl = 'http://' + current_site + relativeLink + "?token=" + str(token)
                email_body = 'Hi '  + \
                             ' Use the link below to verify your email \n' + 'http://localhost:8000/login'
                data = {'email_body': email_body,
                        'email_subject': 'Verify your email'}

                Util.send_email(data)
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)
                return redirect('login')
        context = {'form': form}
        return render(request, 'signup.html', context, status=status.HTTP_201_CREATED)


class VerifyEmail(generics.GenericAPIView):
    def get(self):
        pass


@login_required(login_url='login')
def index(request):
    return render(request, 'index.html')


@login_required(login_url='login')
def calculator(request):
    return render(request, 'calculator.html')


@login_required(login_url='login')
def result(request):
    num1 = int(request.GET["num1"])
    num2 = int(request.GET["num2"])
    num3 = int(request.GET["num3"])
    num4 = int(request.GET["num4"])
    num5 = int(request.GET["num5"])
    num6 = int(request.GET["num6"])
    num7 = int(request.GET["num7"])
    num8 = int(request.GET["num8"])
    num9 = int(request.GET["num9"])
    res = (num1+num2+num3+num4+num5+num6+num7+num8+num9)/9
    med = statistics.median([num1, num2, num3, num4, num5, num6, num7,num8, num9])
    mod = statistics.mode([num1, num2, num3, num4, num5, num6, num7,num8, num9])
    return render(request, 'result.html', {"result": res, "med": med, "mod": mod})


@login_required(login_url='login')
def contact(request):
    return render(request, 'contact.html')


