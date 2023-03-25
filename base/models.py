from django.db import models
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes

from .tokens import email_verification_token


class Newsletter_User(models.Model):

    email = models.CharField(max_length=200)
    excercises_received = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def generate_verification_email(self, request):
        try:
            mail_subject = "Verify your email address"
            message = render_to_string('base/email_templates/template_verification_email.html',
                                       {
                                           'domain': get_current_site(request).domain,
                                           'uid':  urlsafe_base64_encode(force_bytes(self.id)),
                                           'token': email_verification_token.make_token(self),
                                           'protocol': 'https' if request.is_secure() else 'http'
                                       })
            email = EmailMessage(mail_subject, message, to=[self.email])
            return email

        except Exception as e:
            ExceptionTracker.objects.create(
                title='Failed to generate verification email', exception=e)

    def generate_daily_coding_excercise(self, coding_excercise):
        try:
            mail_subject = "Coding Excercise for today"
            message = render_to_string(
                'base/email_templates/template_excercise_email.html')
            email = EmailMessage(mail_subject, message, to=[self.email])
            return email
        except Exception as e:
            ExceptionTracker.objects.create(
                title='Failed to generate daily coding excercise email', exception=e)

    def generate_welcoming_email(self):

        try:
            mail_subject = "Welcome on board!"
            message = render_to_string(
                'base/email_templates/template_welcome_email.html')
            email = EmailMessage(mail_subject, message, to=[self.email])
            return email

        except Exception as e:
            ExceptionTracker.objects.create(
                title='Failed to generate welcoming email', exception=e)

    class Meta:
        ordering = ['-created']

    def __str__(self): return self.email


class Message_contact(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email_contact = models.CharField(max_length=200)
    sent = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    class Meta:
        ordering = ['-sent']

    def __str__(self): return self.message


class CodingExcercise(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    level = models.CharField(max_length=15)
    example_input = models.CharField(max_length=200, null=True, blank=True)
    example_output = models.CharField(max_length=200, null=True, blank=True)
    body = models.CharField(max_length=500)

    def __str__(self): return self.title if self.title else self.body


class ExceptionTracker(models.Model):
    occured = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    exception = models.CharField(max_length=300)

    class Meta:
        ordering = ['-occured']

    def __str__(self): return self.title
