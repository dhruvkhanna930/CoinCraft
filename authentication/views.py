from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from validate_email import validate_email
from django.contrib import messages
# from django.core.mail import EmailMessage
import smtplib as sm
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
from django.urls import reverse

from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site

from .utils import token_generator
from django.contrib import auth

import threading

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error':'username should only contain alphanumeric characters', 'username_vaild':False}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'username in use, choose another one'}, status=409)

        return JsonResponse({'username_vaild':True})
    

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error':'email is invalid', 'email_vaild':False}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'email in use, choose another one'}, status=409)

        return JsonResponse({'email_vaild':True})


class RegisterView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            "fieldValues": request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():

                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html', context )

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save() 

                current_site = get_current_site(request)

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                domain = get_current_site(request).domain
                link = reverse('activate', kwargs= {
                    'uidb64':uidb64, 'token':token_generator.make_token(user)
                })

                activate_url = 'http://+'+domain+link


                # Email Sending Bode Block
                email_subject = 'Activate your CoinCraft Account'
                email_body = f'Hi {user.username}, please use this link to verify your account\n{activate_url}'
                try:
                    smtpserver = sm.SMTP("smtp.gmail.com", settings.EMAIL_PORT)
                    smtpserver.ehlo()
                    smtpserver.starttls()
                    smtpserver.ehlo()
                    smtpserver.login(
                        settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                    from_ = settings.EMAIL_HOST_USER
                    to_ = email
                    message = MIMEMultipart("Alternative")
                    message['Subject'] = email_subject
                    message["From"] = from_
                    message["To"] = email
                    html = f'''
                        <div>{email_body}</div>
                    '''

                    part2 = MIMEText(html, "html")
                    message.attach(part2) 

                    smtpserver.sendmail(from_, to_, message.as_string())

                except Exception as e:
                    print(e)


                messages.success(request, 'Account successfully created')
                return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')
    

class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')
    
class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, f'Welcome, {user.username} you are now logged in')
                    return redirect('expenses')
                
                messages.error(request, f'Account is not active, please check your email')
                return render(request, 'authentication/login.html')
            messages.error(request, f'Invalid credentials, try again')
            return render(request, 'authentication/login.html')
        messages.error(request, f'Please fill all fields')
        return render(request, 'authentication/login.html')



class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, f'You have been logged out')
        return redirect('login')