from django.shortcuts import render, redirect
from django.template import RequestContext
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.decorators import user_passes_test

from .forms import MessageContactForm, NewsletterUserForm
from .models import Newsletter_User, Message_contact
from .tokens import email_verification_token


def home(request):
    form = NewsletterUserForm()
    context = {'form': form}
    if request.method == "POST":
        form = NewsletterUserForm(request.POST)
        email = request.POST.get('email').lower()  
        try:
            validate_email(email)
            try:
                user = Newsletter_User.objects.get(email=email)
                verified = user.verified
                context = {'form': form, 'enrolled': True, 'verified': verified, 'email': email}
                
            except:
                user = Newsletter_User.objects.create(email = email)
                user.save()
                email = user.generate_verification_email(request, user, email)
                return HttpResponseRedirect('email-verification') if email.send() else messages.error("something went wrong")
        except: 
            messages.error(request, "Enter valid email address")

    return render(request, "base/home.html", context=context)



def contact(request):
    form = MessageContactForm()
    if request.method == "POST":
        form = MessageContactForm(request.POST)
        email = request.POST.get('email_contact').lower()
        first_name = request.POST.get('first_name').capitalize()
        last_name = request.POST.get('last_name').capitalize()
        message = request.POST.get('message')
        
        Message_contact.objects.create(
        email_contact=email, 
        first_name=first_name, 
        last_name=last_name, 
        message=message)
        context = {'form': form, 'first_name': first_name}
        return render(request, "base/message_sent.html", context=context)
    
    context = {'form': form}
    return render(request, 'base/contact-page.html', context=context)

def email_verification(request):
    context = {}
    return render(request, 'base/email-verification.html', context=context)

def thankyou_page(request):
    context = {}
    return render(request, 'base/thankyou-page.html', context=context)

def message_sent(request):
    context = {}
    return render(request, 'base/message_sent.html', context=context)

def verify(request, uidb64, token):
    try:
        uid = int(urlsafe_base64_decode(uidb64))
        user = Newsletter_User.objects.get(id=uid)
    except: user = None

    if user and email_verification_token.check_token(user, token): 
        user.verified = True
        user.save()
        return redirect('thank-you')
    else:
        return HttpResponse("Error: Activation link is invalid")


@user_passes_test(lambda u: u.is_superuser)
def resend(request, email):
    user = Newsletter_User.objects.get(email=email)
    email = user.generate_verification_email(request, user, email)
    print('test')
    return HttpResponse('Success: verifiaction email has been sent') if email.send() else HttpResponse('Error: Something went wrong')


def page_not_found(request, exception, template_name='404.html'):
    
    return render(request, template_name, status=404)

