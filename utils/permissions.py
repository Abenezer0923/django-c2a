from apps.accounts.models import User
from django_graphene_permissions.permissions import BasePermission


# def check_permission(user: User):


def is_staff_user(user: User):
    """
    Checks whether given user instance is active and staff member
    """
    return user.is_active and (user.is_staff or user.is_superuser)


class Authenticated(BasePermission):
    """
    Base Permission Class To Check For User Authentication
    @return: True if user is authenticated, False otherwise.
    """


    @staticmethod
    def has_permission(context):
        body = context._body.decode("utf-8")
    
        return (context.user and context.user.is_authenticated )

    # @staticmethod
    # def has_object_permission(context, obj):
    #     print("DEBUG****",obj)
    #     return True




class StaffPermission(BasePermission):
    """
    Permission Class For Authenticating Staff Users
    returns: True for staff users, False otherwise.
    """

    @staticmethod
    def has_permission(context):
        return context.user.is_authenticated and is_staff_user(context.user)





class DeliveryPermission(BasePermission):
    """
    Permission Class For Authenticating Delivery Providers.
    returns: True for delivery provider users and/or superusers, False otherwise.
    """

    @staticmethod
    def has_permission(context):
        user = context.user
        if not user.is_authenticated:
            return False
        try:
            delivery = user.delivery
            if user.is_superuser:
                return True
            return True
        except User.delivery.RelatedObjectDoesNotExist:
            return False



class VendorsPermission(BasePermission):
    """
    Permission Class For Authenticating Vendors
    returns: True for vendors, False otherwise.
    """

    @staticmethod
    def has_permission(context):
        return  (context.user.is_authenticated
            and Vendor.is_vendor(context.user.id)
            or context.user.is_superuser
            or context.user.is_staff
        )

