import graphene
from graphene_django import DjangoObjectType
from django.db.models.functions import Coalesce
from django.db.models import FloatField
from django.db.models import Sum
from utils.permissions import is_staff_user
from . import models
from utils.mixins import PaginatedTypeMixin
from datetime import date
from utils.enums import SubscriptionStatus
from datetime import date
import uuid
from utils import permissions, paginator, exceptions


def resolve_image(img_field, info):
    if not img_field:
        return

    try:
        # img = img_field.file
        return info.context.build_absolute_uri(img_field.url)
    except FileNotFoundError:
        return img_field


class BlogType(DjangoObjectType):
    class Meta:
        model = models.Post
        fields = ("id", "author", "title", "type_of_post",
                  "content", "image", "video")

    def resolve_post(self: models.Post, info):
        return resolve_image(self.image, info)


class BloggerMenuType(DjangoObjectType):
    class Meta:
        model = models.BloggerMenu
        fields = ("id", "blogger", "title", "description")


class VendorDocumentType(DjangoObjectType):
    class Meta:
        model = models.VendorDocument
        # fields = ('id', 'image', 'title', 'description')
        exclude = ("vendor",)

    def resolve_image(self: models.VendorDocument, info):
        return resolve_image(self.image, info)


class VendorAwardType(DjangoObjectType):
    class Meta:
        model = models.VendorAwards
        exclude = ("vendor",)

    def resolve_image(self: models.VendorDocument, info):
        return resolve_image(self.image, info)


class VendorVisitorNumberType(DjangoObjectType):
    class Meta:
        model = models.VendorVisitorNumber
        fields = ("id","count")

 




class VendorBankType(DjangoObjectType):
    class Meta:
        model = models.VendorBank
        exclude = ("vendor",)


class VendorBalanceWithdrawRequestType(DjangoObjectType):
    class Meta:
        model = models.VendorBalanceWithdrawRequest
        
        
class VendorStoreFrontType(DjangoObjectType):
    class Meta:
        model = models.VendorStoreFront


class PaginatedVendorBalanceWithdrawRequestType(PaginatedTypeMixin):
    objects = graphene.List(VendorBalanceWithdrawRequestType)


class VendorBlanceLogType(DjangoObjectType):
    class Meta:
        model = models.VendorBalanceLog


class PaginatedVendorBlanceLogType(PaginatedTypeMixin):
    objects = graphene.List(VendorBlanceLogType)


class VendorsubscriptionPlanType(graphene.ObjectType):
    price = graphene.Float()
    plan = graphene.String()


class AllVendorsubscriptionPlanType(graphene.ObjectType):
    basic = graphene.Field(VendorsubscriptionPlanType)
    gold = graphene.Field(VendorsubscriptionPlanType)
    standard = graphene.Field(VendorsubscriptionPlanType)
    platinum = graphene.Field(VendorsubscriptionPlanType)





class VendorType(DjangoObjectType):
    class Meta:
        model = models.Vendor

        fields = (
            "id",
            "user",
            "store_name",
            "description",
            "store_cover",
            "location",
            "phone",
            "email",
            "video_url",
            "domain",
            "country",
            "region",
            "sub_city",
            "woreda",
            "kebele",
            "trade_licence",
            "trade_name",
            "tin_number",
            "is_supplier",
            "vendorgallery_set",
            "social_links",
            "vendorfooter",
            "reference_code",
            "source_link",
            "support_phone",
            "support_email",
            "banner",
            "logo",
            "catagories",
            "store_locations",
            "template_type",
            "is_active",
            "customer_rating",
            "order_fulfillment_rate",
            "order_quality_score",
            "is_verified",
            "created_at",
            "vendorsubscription_set",
            "follower_set",
            "support_phone_call",
            "vendorsubscription",
            # "store_type",
        )
        
    is_vendor_active = graphene.Boolean()
    legal_documents = graphene.List(VendorDocumentType)
    awards = graphene.List(VendorAwardType)
    bank_info = graphene.Field(VendorBankType)

    order_fulfillment_rate = graphene.String()
    order_quality_score = graphene.String()
    customer_rating = graphene.String()
    product_cont = graphene.Int()
    all_products_count = graphene.Int()
    my_balance = graphene.Float()
    my_total_balance = graphene.Float()
    my_withdraw_requests = graphene.List(VendorBalanceWithdrawRequestType)

    call_action = graphene.String()
    visited_times = graphene.Int(required=False)


  

    def resolve_vendorsubscription_set(self: models.Vendor, info):
        today = date.today()
        return self.vendorsubscription_set.filter(paid=True, end_date__gte=today)

    def resolve_my_withdraw_requests(self: models.Vendor, info):
        return self.vendorbalancewithdrawrequest_set.all()

    def resolve_my_total_balance(self: models.Vendor, info):
        return self.vendorbalancelog_set.filter(balance_type="DEPOSIT").aggregate(
            deposits=Coalesce(Sum("balance", output_field=FloatField()), 0.0)
        )["deposits"]

    def resolve_my_balance(self: models.Vendor, info):
        deposits = self.vendorbalancelog_set.filter(balance_type="DEPOSIT").aggregate(
            deposits=Coalesce(Sum("balance", output_field=FloatField()), 0.0)
        )["deposits"]
        withdraws = self.vendorbalancelog_set.filter(balance_type__in=["WITHDRAW", "FREE_DELIVERY"]).aggregate(
            withdraws=Coalesce(Sum("balance", output_field=FloatField()), 0.0)
        )["withdraws"]

        return max(0, deposits - withdraws)


    def resolve_visited_times(self,info,*args,**kwargs):
        try:
            vendor = models.Vendor.objects.get(id = self.id)
        except models.Vendor.DoesNotExist:
            raise exceptions.GrapheneException("No vendor exists ")

        try:
            countNumber = models.VendorVisitorNumber.objects.filter(vendor = vendor).first()

        except models.VendorVisitorNumber.DoesNotExist:
            raise exceptions.GrapheneException("Vendor Count number does't not exists")


        return countNumber.count

   



    
    def resolve_product_cont(self: models.Vendor, info):
        return self.products.filter().count()

    def resolve_store_cover(self: models.Vendor, info):
        return resolve_image(self.store_cover, info)

    def resolve_banner(self: models.Vendor, info):
        return resolve_image(self.banner, info)

    def resolve_logo(self: models.Vendor, info):
        return resolve_image(self.logo, info)

    def resolve_legal_documents(self: models.Vendor, info):
        return models.VendorDocument.objects.filter(vendor=self)

    def resolve_awards(self: models.Vendor, info):
        return models.VendorAwards.objects.filter(vendor=self)

    def resolve_bank_info(self: models.Vendor, info):
        return models.VendorBank.objects.filter(vendor=self).first()


class VendorPaginatedType(PaginatedTypeMixin):
    objects = graphene.List(VendorType)


class VendorGalleryType(DjangoObjectType):
    class Meta:
        model = models.VendorGallery
        fields = ("id", "image", "img_desc")

    def resolve_image(self: models.VendorGallery, info):
        return resolve_image(self.image, info)


class VendorOverviewDataType(graphene.ObjectType):
    val = graphene.String()
    label = graphene.String()


class OrderSummeryType(graphene.ObjectType):
    """
    describes a single vendor order history
    """

    pending_orders = graphene.Int()
    active_orders = graphene.Int()
    delivered_orders = graphene.Int()
    canceled_orders = graphene.Int()


class DashboardSummeryType(graphene.ObjectType):
    """
    Represents The Vendor Admin Dashboard Overview
    """

    pending_orders = graphene.Int()
    active_orders = graphene.Int()
    delivered_orders = graphene.Int()
    canceled_orders = graphene.Int()

    # suppliers = graphene.Int()
    categories = graphene.Int()
    products = graphene.Int()
    promotions = graphene.Int()

    deleted_products = graphene.Int()
    # active_agent_orders = graphene.Int()

 

class SuppliersDashboardSummeryType(graphene.ObjectType):

    total_orders = graphene.Int()
    followers = graphene.Int()
    products_sold = graphene.Int()
    product_profit = graphene.Int()


class SingleInventoryDataType(graphene.ObjectType):
    stock_amount = graphene.Int()
    sold_amount = graphene.Int()
 


class AllInventoryDataType(graphene.ObjectType):

    result = graphene.List(SingleInventoryDataType)


class SocialLinkType(DjangoObjectType):
    class Meta:
        model = models.SocialLink
        fields = ("id", "facebook", "telegram", "youtube","tiktok","website_url")
        # fields = get_model_field(model)


class PromotionType(DjangoObjectType):
    class Meta:
        model = models.Promotions
        fields = ("id", "image", "size", "label")


class FooterType(DjangoObjectType):
    class Meta:
        model = models.Footer
        interfaces = [graphene.Node]


class VendorFooterType(DjangoObjectType):
    class Meta:
        model = models.VendorFooter
        interfaces = [graphene.Node]
        fields = ("id", "our_service", "trade_service",
                  "our_products", "who_we_are")


class FollowerType(DjangoObjectType):
    class Meta:
        model = models.Follower
        fields = ("id", "user")






class VendorExpirationStatusType(graphene.ObjectType):
    expired = graphene.Boolean()
    days_left = graphene.Int()
    registered_on = graphene.DateTime()
    expires_on = graphene.DateTime()


class VendorPromotionType(DjangoObjectType):
    class Meta:
        model = models.VendorPromotionSubscription


class VendorPromotionPaginatedType(PaginatedTypeMixin):
    objects = graphene.List(VendorPromotionType)




