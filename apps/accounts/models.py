from email.policy import default
from enum import unique
import os
import re
import random
import string
from statistics import mode
from datetime import timedelta
from typing import Dict
from uuid import uuid4
from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_save
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from utils import methods
from utils.mixins import BaseModelMixin
from django.conf import settings
from utils.jsons import to_dict
from django.contrib.auth.models import AbstractUser,Group,Permission



def generate_reference_code():
    code = str(uuid4()).replace("-", "")[:6]
    return code


NULL = {"null": True, "blank": True}


class UserManager(BaseUserManager):
    def create(self, username, **kwargs):
        if username is None:
            raise ValueError("username can not be null")

        user = self.model(username=username, **kwargs)
        user.set_password(kwargs.get("password"))
        user.save(using=self._db)
        return user

    def create_superuser(self, username, **kwargs):
        kwargs["is_staff"] = True
        kwargs["is_superuser"] = True
        kwargs["is_verified"] = True
        return self.create(username=username, **kwargs)

    def create_user(self, username, **kwargs):
        return self.create(username=username, **kwargs)


def rand():
    not_unique = False
    while not_unique:
        unique_ref = "".join(
            [random.choice(string.ascii_uppercase + string.digits)
             for x in range(10)]
        )
        if not User.objects.filter(referral_code=unique_ref):
            not_unique = False
    return not_unique

    # return "".join(
    #     [random.choice(string.ascii_uppercase + string.digits) for x in range(10)]
    # )


class User(AbstractBaseUser, PermissionsMixin, BaseModelMixin):
    """
    Base User Model For China to Africa Project
    """
  
    # blank=True,
    gender_values = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    first_name = models.CharField(max_length=50, **NULL)
    last_name = models.CharField(max_length=50, **NULL)
    username = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15, unique=True, **NULL)
    email = models.EmailField(unique=False,**NULL)
    profile_pic = models.ImageField(upload_to="profile/pics", **NULL)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    last_login = models.DateTimeField(**NULL)
    date_joined = models.DateTimeField(default=timezone.localtime)
    _role = [
        ("CUSTOMER", "CUSTOMER"),
        ("SALES", "SALES"),
        ("DEVELOPER", "DEVELOPER"),
        ("ACCOUNT_MANAGER", "ACCOUNT_MANAGER"),
        ("ADMIN", "ADMIN"),
        ("SUPER_ADMIN", "SUPER_ADMIN"),
        ("CUSTOMER_SERVICE", "CUSTOMER_SERVICE"),
        ("MARKETING", "MARKETING"),
        ("CONTENT_MANAGER", "CONTENT_MANAGER"),
    ]
    role = models.CharField(max_length=60, choices=_role, default="CUSTOMER")
    old_phone = models.CharField(max_length=15, unique=True, **NULL)
    age =  models.IntegerField(blank = True,null = True)
    gender = models.CharField(max_length = 100,choices = gender_values,blank = True,null = True)

    USERNAME_FIELD = "username"

    objects = UserManager()

    def __str__(self):
        return self.username



    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

 
class ResetCode(BaseModelMixin):
    """
    Stores Codes That Are Sent By Email For Users For Password Reset
    """

    user = models.ForeignKey(User, models.CASCADE, **NULL)
    email = models.EmailField(**NULL)
    phone = models.CharField(max_length=15, unique=False, **NULL)
    code = models.CharField(max_length=10, default=methods.reset_code)

    class Meta:
        unique_together = ["user", "phone"]

    def __str__(self):
        return f"{self.user} - {self.code}"


class EmailSubscription(BaseModelMixin):
    """
    Adding Email Subscription model
    This model allows to store subscriber emails
    """

    email = models.EmailField(max_length=255, unique=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ("-created_at",)








class ReferralCodeType(BaseModelMixin):
    """
    Reference Code Type
    """

    is_active = models.BooleanField(default=True)
    points = models.PositiveIntegerField(default=0)
    _types = [("SIGNUP", "SIGNUP"), ("ORDER", "ORDER")]
    type = models.CharField(max_length=60, choices=_types, default="SIGNUP")

    def __str__(self) -> str:
        return f"{self.type} - {self.points}"


def add_to_two():
    return timezone.localtime() + timedelta(seconds=180)








class NotificationHistory(BaseModelMixin):
    """
    Notification History
    """

    received_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notify", null=True, blank=True
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField()
    _types = [("SINGLE", "SINGLE"), ("GROUP", "GROUP"), ("CART", "CART")]
    type = models.CharField(max_length=60, choices=_types, default="SINGLE")


class NotificationSchedule(BaseModelMixin):
    """
    Notification History
    """

    title = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField()
    _types = [
        ("ONE_TIME", "ONE_TIME"),
        ("WEEK", "WEEK"),
        ("MONTH", "MONTH"),
        ("EVERY_DAY", "EVERY_DAY"),
    ]
    type = models.CharField(max_length=60, choices=_types, default="ONE_TIME")
    _notification_types = [
        ("USER", "USER"),
        ("VENDOR", "VENDOR"),
        ("SINGLE_USER", "SINGLE_USER"),
    ]
    time = models.TimeField(null=False, blank=False)
    single_user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE
    )
    notification_type = models.CharField(
        max_length=60, choices=_notification_types, default="USER"
    )


class HelpVideo(BaseModelMixin):
    title = models.CharField(max_length=255, null=True, blank=True)
    video_url = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class RolePermission(BaseModelMixin):
    """
    Role Permission
    """

    name = models.CharField(max_length=255, unique=True)
    resources = models.JSONField(default=dict)
