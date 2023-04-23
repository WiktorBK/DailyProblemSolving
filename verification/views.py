from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.validators import validate_email
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError

from base.forms import MessageContactForm, NewsletterUserForm
from base.models import Newsletter_User, MessageContact, ExceptionTracker, CodingExcercise
from codingroutine.tokens import email_verification_token, unsubscribe_token
from codingroutine.functions import *


def email_verification(request):
    context = {}
    return render(request, 'verification/email-verification.html', context=context)

def verify(request, uidb64, token):
    try:
        uid = int(urlsafe_base64_decode(uidb64))
        user = Newsletter_User.objects.get(id=uid)
    except: user = None

    if user and email_verification_token.check_token(user, token): 
        user.verified = True
        user.save()
        welcoming_email = user.generate_welcoming_email()

        try:
            welcoming_email.send()
        except Exception as e: 
            ExceptionTracker.objects.create(title='Failed to send welcoming email', exception=e)

        return redirect('thank-you')
    else:
        return HttpResponse("Error: Activation link is invalid")

def unsubscribe(request, uidb64, token):
    try:
        uid = int(urlsafe_base64_decode(uidb64))
        user = Newsletter_User.objects.get(id=uid)
    except: return HttpResponse("Error: Activation link is invalid")
    
    if user and user.unsubscribe_token == token:
        user.active = False
        user.verified = False
        user.save()
    else: return HttpResponse("Error: Activation link is invalid")

    return render(request, "verification/unsubscribe-page.html")

@user_passes_test(lambda u: u.is_superuser)
def resend(request, email):
    try: 
        user = Newsletter_User.objects.get(email=email)
        email = user.generate_verification_email(request)
    
        return HttpResponse('Success: verifiaction email has been sent') if email.send() else HttpResponse('Error: Something went wrong')
    except Exception as e: 
        ExceptionTracker.objects.create(title="Failed to resend verification link", exception=e)
        return HttpResponse('Error: verifiaction email could not be sent')