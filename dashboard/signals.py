from allauth.socialaccount.signals import social_account_added, pre_social_login
from allauth.socialaccount.models import SocialLogin
from allauth.exceptions import ImmediateHttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.dispatch import receiver
from django.conf import settings


ALLOWED_EMAILS = getattr(settings, 'GOOGLE_ALLOWED_EMAILS', [])


@receiver(pre_social_login)
def check_google_email(sender, request, sociallogin, **kwargs):
    if not ALLOWED_EMAILS:
        return
    email = sociallogin.account.extra_data.get('email', '')
    if email not in ALLOWED_EMAILS:
        raise ImmediateHttpResponse(redirect('/login/?error=notallowed'))
