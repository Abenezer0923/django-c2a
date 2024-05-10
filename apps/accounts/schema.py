from cmath import inf
import re
from tracemalloc import start
from typing import Optional
from django.db.models.query_utils import Q
import graphene
from django_graphene_permissions import permissions_checker

from . import models, types
from utils import permissions, paginator, enums
from django.db.models import Sum, F, Value as V
from django.db.models.functions import Concat
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from utils import exceptions

POINTS_REQUIRED_TO_WITHDRAW = 2000


class FilterUserInput(graphene.InputObjectType):
    username = graphene.String()
    user_id = graphene.UUID()


class UsersPointHistoryFilter(graphene.InputObjectType):
    qualified_to_withdraw = graphene.Boolean(False)
    filter_zero_points = graphene.Boolean(default_value=True)


class UsersPointHistoryLogFilter(graphene.InputObjectType):
    log_type = graphene.String()
    created_with_in = graphene.Argument(enums.CreatedWithIn)


class Query(graphene.ObjectType):
    all_users = graphene.Field(
        types.PaginatedUserType,
        page=graphene.Int(1),
        filters=FilterUserInput(),
    )
    get_user_by_id = graphene.Field(types.UserType, username=graphene.String())
    get_me = graphene.Field(
        types.UserType,
    )
    user_verified = graphene.Boolean(email=graphene.String(required=True))
    
   

   
    active_users = graphene.Field(
        types.PaginatedUserType,
        page=graphene.Int(1),
        per_page=graphene.Int(25),
    )

    logged_in_users = graphene.Field(
        types.PaginatedUserType,
        page=graphene.Int(1),
        filter=FilterUserInput(),
    )
    search_users = graphene.Field(
        types.PaginatedUserType,
        page=graphene.Int(1),
        per_page=graphene.Int(10),
        search=graphene.String(),
        start_date=graphene.String(),
        end_date=graphene.String(),
    )
    staff_users = graphene.Field(
        types.PaginatedUserType,
        page=graphene.Int(1),
        per_page=graphene.Int(10),
        search=graphene.String(),
        role=graphene.String(),
    )
 
    role_permissions = graphene.Field(
        types.RolePermissionType,
        role=graphene.String(),
    )
    get_all_role_permissions = graphene.Field(
        graphene.List(types.RolePermissionType),
    )

    @permissions_checker([permissions.StaffPermission])
    def resolve_gift_cards_history(self, info, page, per_page, search, **kwargs):
        qs = models.GiftCard.objects.filter(used_amount__gt=0)

        if search:
            qs = qs.filter(
                Q(created_by__first_name__icontains=search)
                | Q(gift_password__icontains=search)
            )

        return paginator.common_pagination(qs, page=page, per_page=per_page)


    @permissions_checker([permissions.StaffPermission])
    def resolve_get_notification_schedule(self, info, id):
        return models.NotificationSchedule.objects.get(id=id)


    def resolve_get_all_role_permissions(self, info, **kwargs):
        return models.RolePermission.objects.all()

    @permissions_checker([permissions.StaffPermission])
    def resolve_role_permissions(self, info, role, **kwargs):
        return models.RolePermission.objects.get(role=role)

    @permissions_checker([permissions.StaffPermission])
    def resolve_help_videos(self, info, **kwargs):
        return models.HelpVideo.objects.all()


    def resolve_staff_users(cls, info, page, per_page, search, role, **kwargs):
        qs = models.User.objects.filter(is_staff=True)

        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )

        if role:
            qs = qs.filter(role=role)
        return paginator.common_pagination(qs, page=page, per_page=per_page)

   
    def resolve_users_point_history_log(
        self,
        info,
        page,
        filters: Optional[UsersPointHistoryLogFilter] = None,
    ):
        qs = models.PointsHistory.objects.all()

        if filters:
            if filters.log_type:
                qs = qs.filter(type=filters.log_type)

            if filters.created_with_in:
                now = timezone.now()
                created_at__gt = now - timedelta(hours=filters.created_with_in)
                qs = qs.filter(created_at__gt=created_at__gt)

        return paginator.common_pagination(qs, page=page)

    def resolve_search_users(cls, info, page, per_page, search, **kwargs):
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        qs = models.User.objects.annotate(
            full_name=Concat("first_name", V(" "), "last_name")
        ).filter(
            Q(full_name__icontains=search)
            | Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
        )
        if start_date and end_date:
            if start_date == end_date:
                start_date = start_date.split("T")[0]
                qs = qs.filter(date_joined__date=start_date)
            else:
                qs = qs.filter(date_joined__range=[start_date, end_date])
        return paginator.common_pagination(qs, page=page, per_page=per_page)


  
    @classmethod
    def resolve_user_verified(cls, root, info, email):
        try:
            user = models.User.objects.get(email=email)
            return user.is_verified
        except models.User.DoesNotExist:
            return False

    @classmethod
    def resolve_get_user_by_id(cls, root, info, username):
        try:
            user = models.User.objects.get(username=username)
            return user
        except models.User.DoesNotExist:
            raise exceptions.GrapheneException(f"user not found !")



 



    def resolve_logged_in_users(self, info, page, **kwargs):
        objects = info.context.online_now or []
        return paginator.common_pagination(objects, page=page)

 
   
    def resolve_all_users(self, info, page, **kwargs):
        """
        @permission: AdminPermission

        @return: all user Objects (Paginated).
        """

        # Create your views here.

        import requests

        user = User.objects.filter(username="hiruy")
        # social = user.social_auth.get(provider='google-oauth2')
        # response = requests.get(
        #     'https://www.googleapis.com/plus/v1/people/me/people/visible',
        #     params={'access_token': social.extra_data['access_token']}
        # )
        # friends = response.json()['items']

        if kwargs.get("filter"):
            username = kwargs.get("filter").username
            objects = models.User.objects.filter(
                Q(username=username) | Q(phone=username) | Q(email=username)
            ).order_by("-created_at")

        else:
            objects = models.User.objects.all().order_by('-created_at')

        return paginator.common_pagination(objects, page=page)

    @permissions_checker([permissions.Authenticated])
    def resolve_get_me(self, info):
        """
        @permission: Authenticated

        @return: currently Authenticated User Object
        """
        # from django.utils import timezone
        # from datetime import datetime, timedelta

        # x = timezone.localtime() + timedelta(seconds=180)
        # # x += timedelta(seconds=63)
        # print(timezone.localtime(), x, "-------social")
        return info.context.user


    def resolve_users_point_history_log(
        self,
        info,
        page,
        filters: Optional[UsersPointHistoryLogFilter] = None,
    ):
        qs = models.PointsHistory.objects.all()

        if filters:
            if filters.log_type:
                qs = qs.filter(type=filters.log_type)

            if filters.created_with_in:
                now = timezone.now()
                created_at__gt = now - timedelta(hours=filters.created_with_in)
                qs = qs.filter(created_at__gt=created_at__gt)

        return paginator.common_pagination(qs, page=page)

