from cmath import inf
import email
from email import message
from email.policy import default
from hashlib import shake_128
from itertools import product
from math import prod
from multiprocessing import context
import graphene
from django_graphene_permissions import permissions_checker
from django.core.mail import EmailMessage, send_mail
from django.template.loader import get_template
from utils.jsons import to_dict
from . import models, types
from utils import permissions, exceptions, mixins
from graphql_jwt.shortcuts import get_token
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate, login
from django.db.models import Q, Sum
from django.forms.models import model_to_dict


from apps.accounts.models import User
import random
import string





import graphql_social_auth
from django.contrib.auth import authenticate
from django.utils import timezone
import random
import string
from math import prod
from multiprocessing import context
import graphene
from utils.validators import Stringy, escape_str, is_valid_phone_number
# from utils.sms_providers import AfroSms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

import datetime
import requests
import json
import re
from rest_framework.authtoken.models import Token
from django.http import HttpResponse



class DeleteMyAccount(graphene.Mutation):
    deleted = graphene.Boolean()

    @permissions_checker([permissions.Authenticated])
    def mutate(self, info, **kwargs):
        try:
            user = info.context.user
            user.is_active = False
            user.is_staff = False
            user.is_verified = False
            user.is_superuser = False
            user.old_phone = user.phone
            user.phone = "".join(
                [
                    random.choice(string.ascii_uppercase + string.digits)
                    for x in range(10)
                ]
            )
            user.email = "".join(
                [
                    random.choice(string.ascii_uppercase + string.digits)
                    for x in range(10)
                ]
            )
            user.username = "".join(
                [
                    random.choice(string.ascii_uppercase + string.digits)
                    for x in range(10)
                ]
            )
            user.save()
            return DeleteMyAccount(True)
        except:
            return DeleteMyAccount(False)





import random

def generate_otp(length=6):
  """Generates a random OTP of specified length."""

  digits = "0123456789"
  otp = ""

  for _ in range(length):
    otp += random.choice(digits)

  return otp



def generate_username():
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(8))  

class UserSignupMutation(graphene.Mutation):
    """
    create a new user (Signup)

    @permission: None
    """

    class Arguments:
        username, password = [graphene.String(required=True) for _ in range(2)]
        username = graphene.String(required=False)
        first_name, last_name, phone, email = [
            graphene.String(required=True) for _ in range(4)
        ]
        phone, email = [
            graphene.String(required=False) for _ in range(2)
        ]
        date_of_birth = graphene.Date(required  = False)
        gender = graphene.String(required = False)
        profile_pic = mixins.ImageScalar()
        is_buyer = graphene.Boolean(True)
      

        phone = graphene.String(required=True)
        is_app = graphene.Boolean(False)
    

    payload = graphene.Field(types.UserType)
    token = graphene.String()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        kwargs["username"] = kwargs["username"].lower()
        is_buyer = kwargs.pop("is_buyer")
        phone = kwargs.pop("phone", "")
    

        try:
            models.User.objects.get(username=kwargs["username"])
            raise exceptions.GrapheneException(
                f'user with username {kwargs["username"]} already exists!'
            )
        except models.User.DoesNotExist:
            if phone:
                user = models.User.objects.filter(phone=phone)
                if user:
                    raise exceptions.GrapheneException(
                        f"user with phone {phone} already exists!"
                    )
            
            
            user = models.User.objects.create(
                first_name = kwargs.get('first_name'),
                last_name = kwargs.get('last_name'),
                username = kwargs.get('username'),
                phone = phone,
                email = kwargs.get('email'))
            
            
    
            user.save()
            return UserSignupMutation(payload=user, token=get_token(user))


class VerifyUser(graphene.Mutation):
    """
    Verify User With otp
    """

    class Arguments:
        phone = graphene.String()
        code = graphene.String(required=True)
        verify_user = graphene.Boolean(True)

    verified = graphene.Boolean()


    def mutate(self, info, **kwargs):
        phone = kwargs.get("phone", None)
        if phone and not is_valid_phone_number(phone):
            raise exceptions.GrapheneException("Invalid Phone number format")
          
            

        if kwargs.get("verify_user"):
            try:
                if phone:
                    user = models.User.objects.get(phone=phone)
                elif kwargs.get("email"):
                    user = models.User.objects.get(email=kwargs.get("email"))
                else:
                    user = models.User.objects.get(phone=phone)
            except models.User.DoesNotExist: 
                raise exceptions.GrapheneException("User not found")
            import logging
            logging.warning(phone)
            logging.warning(kwargs.get("email"))
            logging.warning(user)
            logging.warning(kwargs["code"])
            code = models.ResetCode.objects.filter(
                Q(email=kwargs.get("email")) | Q(phone=phone),
                code=kwargs["code"],
                user=user,
            )

            if not code.exists() :
                raise exceptions.GrapheneException("Invalid Or Expired Code")
            
            current_datetime = datetime.datetime.now() - datetime.timedelta(minutes=5)
            if  code.first().created_at.timestamp() < current_datetime.timestamp():
                code.delete()
                raise exceptions.GrapheneException("Invalid Or Expired Code")
                

            user.is_verified = True
            user.save()
            user.verify()
            token = Token.objects.create(user=user)
            response = HttpResponse("Mutation complete!")
            response.set_cookie('user_token', token, max_age=3600)

        else:
            code = models.ResetCode.objects.filter(
                Q(email=kwargs.get("email")) | Q(phone=phone), code=kwargs["code"]
            )

        if not code.exists():
            raise exceptions.GrapheneException("Invalid Or Expired Code")
        
        current_datetime = datetime.datetime.now() - datetime.timedelta(minutes=1)
        if  code.first().created_at.timestamp() < current_datetime.timestamp():
            code.delete()
            raise exceptions.GrapheneException("Invalid Or Expired Code")

        code.delete()
        return VerifyUser(True)









class CustomAuthToken(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    payload = graphene.Field(types.UserAuthType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        username = kwargs.get("username").lower()
        q_filter = Q(
            _connector="OR",
            username__exact=username,
            phone__exact=username,
            email__exact=username,
        )
        try:
            users = models.User.objects.filter(q_filter)
            # print(users, "-------user")
            for user in users:
                if not user.check_password(kwargs.get("password")):
                    continue
                if not user.is_verified:
                    raise exceptions.GrapheneException(
                        "User Not Verified", 400)

                if user.check_password(kwargs.get("password")):
                    _user = authenticate(
                        username=user.username, password=kwargs.get("password")
                    )
                    if _user:
                        return CustomAuthToken({"user": user, "token": get_token(user)})
            raise exceptions.GrapheneException(
                "Incorrect Credentials Provided", 401)
        except models.User.DoesNotExist:
            raise exceptions.GrapheneException(
                "Incorrect Credentials Provided")









class UserSignupOTPMutation(graphene.Mutation):
    """
    create a new user with otp(Signup)

    @permission: None
    """

    class Arguments:
        first_name, phone = [graphene.String(required=True) for _ in range(2)]
        last_name,username = [graphene.String() for _ in range(2)]
        profile_pic = mixins.ImageScalar()
        referral_code = graphene.String()
        email = graphene.String(required = True)
        is_app = graphene.Boolean(False)
        is_buyer = graphene.Boolean(False)
        is_telebirr_user = graphene.Boolean(False)

    payload = graphene.Field(types.UserType)
    token = graphene.String()
   

    @classmethod
    def mutate(cls, root, info, phone, is_telebirr_user, is_app, **kwargs):
        referred_code = None
        afro_sms_api = AfroSMS()
        
        if kwargs.get("referral_code"):
            referred_code = (
                f"APP_{kwargs.pop('referral_code')}"
                if is_app
                else f"WEB_{kwargs.pop('referral_code')}"
            )
        if not phone:
            raise exceptions.GrapheneException("phone number required!!")

        if phone and not is_valid_phone_number(phone):
            # phone = AfroSMS.format_phone(phone)
            raise exceptions.GrapheneException("phone not formatted!!")

        while True:
            username = generate_username()
            kwargs["username"] = f"user_{username}"
            try:
                models.User.objects.get(username=kwargs["username"])
            except models.User.DoesNotExist:
                break

        if kwargs.get("email"):
            user = models.User.objects.filter(email=kwargs.get("email"))
            if user:
                raise exceptions.GrapheneException(
                    f'user with email {kwargs["email"]} already exists!'
                )
        is_buyer = kwargs.pop("is_buyer")
        if phone:
            user = models.User.objects.filter(phone=phone)
            if user:
                raise exceptions.GrapheneException(
                    f"user with phone {phone} already exists!")
        
        phone = afro_sms_api.format_phone(phone)
        user = models.User.objects.create(phone=phone, referred_code=referred_code, **kwargs)
        send_status, send_data = afro_sms_api.send_otp(phone)
        # user.save()

        if send_status:
            code = models.ResetCode.objects.create(user = user,email=email,phone = phone,code=send_data.get("code"))


        user.is_verified = is_telebirr_user
        user.save()
        if is_telebirr_user:
            user.verify()
        return UserSignupOTPMutation(payload=user, token=get_token(user))


class VerifyUserOTPMutation(graphene.Mutation):
    """
    Verify User Phone
    """

    class Arguments:
        # phone, password = [graphene.String(required=False) for _ in range(2)]
        phone = graphene.String()
        otp = graphene.String()

    payload = graphene.Field(types.UserType)
    token = graphene.String()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        phone = kwargs.get("phone", "")
        otp = kwargs.get("otp","")
        current_datetime = datetime.datetime.now() - datetime.timedelta(minutes=5)


        try:
            if phone:
                user = models.User.objects.get(phone=phone)
        
           
            try:
                code = models.ResetCode.objects.filter(user=user,phone = phone)
               
            except models.ResetCode.DoesNotExist:
                raise exceptions.GrapheneException("invalid otp cuz reset code not found")

            if code.first() != None:
                if  code.first().created_at.timestamp() < current_datetime.timestamp():
                    code.first().delete()
                    raise exceptions.GrapheneException("Invalid Or Expired Code")
            else:
                raise exceptions.GrapheneException("no reset code")
            if code is not None and code.first().code == kwargs.get("otp"):
                user.is_verified = True
                user.save()
                return VerifyUserOTPMutation(payload = user,token=get_token(user))
            else :
                raise exceptions.GrapheneException("invalid otp")
        
        except models.User.DoesNotExist:
            raise exceptions.GrapheneException("phone not found")
        for code in models.ResetCode.objects.all():
                code.delete()
        return VerifyUserOTPMutation(payload = user,token=get_token(user))

class UpdateUserMutation(graphene.Mutation):
    """
    Update Existing Authenticated User

    @permission: Authenticated
    """

    class Arguments:
        username, first_name, last_name, phone, email, language = [
            graphene.String() for i in range(6)
        ]
        old_password, new_password1, new_password2 = [
            graphene.String() for _ in range(3)
        ]
        profile_pic = mixins.ImageScalar()
        # email = Stringy(validate="^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$")
        # phone = Stringy(validate="^\+251[0-9\s]{9}$")

    payload = graphene.Field(types.UserType)

    @permissions_checker([permissions.Authenticated])
    def mutate(self, info, **kwargs):
        user: models.User = info.context.user
        old_email = user.email
        phone = (
            afro_sms_api.format_phone(kwargs.pop("phone", ""))
            if kwargs.get("username")
            else None
        )

        try:
            if kwargs.get("username"):
                _user = models.User.objects.get(
                    ~Q(id=user.id), username=kwargs.get("username")
                )
                if _user != user:
                    raise exceptions.GrapheneException(
                        "username already exist")
        except models.User.DoesNotExist:
            user.username = kwargs.get("username") or user.username

        try:
            if phone:
                _user = models.User.objects.get(~Q(id=user.id), phone=phone)
                raise exceptions.GrapheneException(
                    f'user with phone {kwargs["phone"]} already exists!'
                )
        except models.User.DoesNotExist:
            user.phone = phone or user.phone

        try:
            if kwargs.get("email"):
                _user = models.User.objects.get(
                    ~Q(id=user.id), email=kwargs.get("email")
                )
                raise exceptions.GrapheneException(
                    f'user with email {kwargs["email"]} already exists!'
                )
        except models.User.DoesNotExist:
            user.email = kwargs.get("email") or user.email

        user.first_name = kwargs.get("first_name") or user.first_name
        user.last_name = kwargs.get("last_name") or user.last_name

        phone = kwargs.get("phone", "")
        if kwargs.get("phone") and not is_valid_phone_number(phone):
            phone = AfroSMS.format_phone(phone)

        user.phone = phone or user.phone
        user.email = kwargs.get("email") or user.email
        user.profile_pic = kwargs.get("profile_pic") or user.profile_pic
        user.language = kwargs.get("language") or user.language

        if kwargs.get("old_password") and user.check_password(kwargs["old_password"]):
            if kwargs.get("new_password1") != kwargs.get("new_password2"):
                raise exceptions.GrapheneException("Passwords Don't Match")
            try:
                validate_password(kwargs.get("new_password1"), user)
            except ValidationError as e:
                raise exceptions.GrapheneException(" ".join(e))
            user.set_password(kwargs["new_password1"])

        elif kwargs.get("old_password"):
            raise exceptions.GrapheneException("Incorrect Old Password")

        user.save()

        return UpdateUserMutation(user)


      


class Mutation(graphene.ObjectType):
    user_auth = CustomAuthToken.Field()
    user_signup = UserSignupMutation.Field()
    update_profile = UpdateUserMutation.Field()
    verify_user = VerifyUserOTPMutation.Field()
 
  








