from statistics import mode
import graphene
from graphene_django import DjangoObjectType
from utils.mixins import PaginatedTypeMixin
from django.core.cache import cache
from . import models
from django.db.models import F


def resolve_image(img_field, info):
    if not img_field:
        return

    try:
        # img = img_field.file
        return info.context.build_absolute_uri(img_field.url)
    except FileNotFoundError:
        return img_field




class UserType(DjangoObjectType):
    class Meta:
        model = models.User

        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "phone",
            "email",
            "profile_pic",
            "is_active",
            "is_verified",
            "user_permissions",
            "is_staff",
            "is_superuser",
            "language",
            "updated_at",
            "role",
            "gender",
        
        )

    permissions = graphene.List(graphene.String)

 

    def resolve_wallet(self, info):
        return models.Wallet.objects.filter(user__id=self.id).first()

    def resolve_permissions(self: models.User, info):
        return self.user_permissions.all()

    def resolve_profile_pic(self: models.User, info):
        return resolve_image(self.profile_pic, info)
  

    
    


    equivalent_etb = graphene.Int()

    def resolve_equivalent_etb(self, info):
        return int(self.points * .1)

class PaginatedUserType(PaginatedTypeMixin):
    objects = graphene.List(UserType)
    






class UserAuthType(graphene.ObjectType):
    token = graphene.String()
    user = graphene.Field(UserType)


class RequestVerificationCodeType(graphene.ObjectType):
    code_sent = graphene.String()
    code = graphene.String()


class RolePermissionType(DjangoObjectType):
    class Meta:
        model = models.RolePermission
