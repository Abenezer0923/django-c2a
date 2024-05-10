from django.core.mail import send_mail
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from . import models
from threading import Thread
from utils.sms_providers import PurposeSMS
from django.core.management import call_command
from django.conf import settings
from utils import exceptions
import random
import string
import ast





@receiver(post_save, sender=models.User)
def send_otp_when_user_registered(sender, instance: models.User, created: bool, **kwargs):
    if created:
        phone = instance.phone
        if phone:
            status_code,otp = PurposeSMS().send_otp(phone)
            models.ResetCode.objects.create(user = instance,email = instance.email,phone = phone,code = otp)
            if status_code== 200:
                models.ResetCode.objects.create(user = instance,email = instance.email,phone = phone,code = otp)
            


