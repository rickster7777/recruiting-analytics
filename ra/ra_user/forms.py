from random import randint, random
import sendgrid
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils import timezone
# from django.contrib.sites.models import Site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.response import Response

from ra.settings.config_ra import main_conf as config

from .models import UserOtp

UserModel = get_user_model()


def send_email(context):
    """
    Send Email for Reset Password Functionality
    """
    site_url = context['domain']

    otp_link = "{0}://{1}/verify-otp/".format(
        context['protocol'], site_url)

    to_email = context['email']

    from_email = 'noreply@RecruitingAnalytics.com'

    if 'qa' in site_url:
        sg = sendgrid.SendGridAPIClient(config.get('QA_SENDGRID_APIKEY'))
        template_id = "d-95620ef58d1346dd8b187f0288402bc8"
    else:
        sg = sendgrid.SendGridAPIClient(config.get('SENDGRID_APIKEY'))
        template_id = "d-114ce1cdfca04245a4c8ad56b4e77913"

    data = {
        "dynamic_template_data": {
            "user":
                context['user'].first_name
                if context['user'].first_name
                else context['user'].username,
            "otp_link": otp_link,
        },
        "from": {
            "email": from_email,
        },
        "personalizations": [
            {
                "to": [
                    {
                        "email": to_email,
                        "name": context['user'].first_name
                        if context['user'].first_name
                        else context['user'].username,
                    }
                ],
                "dynamic_template_data": {
                    "user":
                        context['user'].first_name
                        if context['user'].first_name
                        else context['user'].username,
                    "otp_link": otp_link,
                    'otp': context['otp'],
                },
            }
        ],
        "template_id": template_id
    }
    return sg.client.mail.send.post(request_body=data)


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=350)
    domain = forms.CharField(label=_("Domain"), max_length=350)

    def get_users(self, email):

        active_users = UserModel._default_manager.filter(**{
            '%s__iexact' % UserModel.get_email_field_name(): email,
            'is_active': True,
        })
        return (u for u in active_users if u.has_usable_password())

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
            Generate a one-use only link for resetting password and send it
            to the user.
        """

        email = self.cleaned_data["email"]
        domain = self.cleaned_data["domain"]
        try:
            user = UserModel.objects.get(email__iexact=email)
            verify_user = UserOtp.objects.filter(user__email__iexact=email)
            if verify_user:
                if verify_user[0].verified == True:
                    otp = randint(10000, 99999)
                    verify_user[0].otp = otp
                    verify_user[0].created_at = timezone.now()
                    verify_user[0].expired_on = timezone.timedelta(minutes=15)
                    verify_user[0].verified = False
                    verify_user[0].save()
                    otp = verify_user[0].otp

                elif verify_user[0].expired_on < timezone.now():
                    otp = randint(10000, 99999)
                    verify_user[0].otp = otp
                    verify_user[0].created_at = timezone.now()
                    verify_user[0].save()
                    otp = verify_user[0].otp
                else:
                    if not verify_user[0].expired_on < timezone.now() + \
                            timezone.timedelta(minutes=15):
                        otp = randint(10000, 99999)
                        verify_user[0].created_at = timezone.now()
                        verify_user[0].expired_on = timezone.timedelta(
                            minutes=15)
                        verify_user[0].save()
                        otp = verify_user[0].otp
                    else:
                        verify_user[0].created_at = timezone.now()
                        verify_user[0].expired_on = timezone.timedelta(
                            minutes=15)
                        verify_user[0].verified = False
                        verify_user[0].save()
                        otp = verify_user[0].otp
            else:
                otp = randint(10000, 99999)
                user_otp = UserOtp.objects.create(user=user, otp=otp)
                otp = user_otp.otp
            for user in self.get_users(email):
                context = {
                    'email': email,
                    'domain': domain,
                    'otp': otp,
                    'user': user,
                    'protocol': 'https' if use_https else 'http',
                }
                send_email(context)

        except Exception as e:
            return Response(
                {
                    "detail": ("Email is Invalid."),
                }
            )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not UserModel.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError(
                "There is no user registered with the specified email address!")

        return email


class CustomSetPasswordForm(SetPasswordForm):
    otp = forms.IntegerField()
