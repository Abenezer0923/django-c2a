from statistics import mode
import graphene
from django_graphene_permissions import permissions_checker
from . import models, types
from utils import permissions, paginator, exceptions
from django.utils import timezone
from datetime import timedelta, date
from utils.paginator import common_pagination

# import logging
from pathlib import Path
from time import time
from functools import partial
import os
from concurrent.futures import ProcessPoolExecutor
from PIL import Image

from django.db.models import Q

from utils.enums import CreatedWithIn

from . import inputs
from django.db.models import Case, When, Value, CharField,F
from django.db.models.functions import  ExtractDay
from django.utils import timezone


class Query(graphene.ObjectType):
    # queries with unit test case
    get_blog_post = graphene.List(types.BlogType)
    
    # non-tested queries
    get_detail_post = graphene.Field(types.BlogType, id=graphene.UUID(required=True))

    vendor_dashboard_summery = graphene.Field(types.DashboardSummeryType)
    supplier_dashboard_summery = graphene.Field(types.SuppliersDashboardSummeryType)
    inventory_management_summary = graphene.Field(types.AllInventoryDataType)
    vendor_data = graphene.Field(types.VendorType)
    vendor_gallery = graphene.List(
        types.VendorGalleryType, store_name=graphene.String(required=True)
    )

    get_footer = graphene.List(types.FooterType)
    get_vendor_footer = graphene.List(types.VendorFooterType)
    get_vendor_followers = graphene.List(
        types.FollowerType, vendor_id=graphene.UUID(required=True)
    )

    suppliers = graphene.List(types.VendorType)
    supplier = graphene.Field(types.VendorType, id=graphene.UUID(required=True))

    retailers = graphene.List(types.VendorType)
    retailer = graphene.Field(types.VendorType, id=graphene.UUID(required=True))

    blogger_menu = graphene.List(
        types.BloggerMenuType, blogger_id=graphene.UUID(required=True)
    )
    vendor_social_link = graphene.Field(
        types.SocialLinkType, vendor_id=graphene.UUID(required=True)
    )

    all_vendors = graphene.Field(
        types.VendorPaginatedType,
        page=graphene.Int(1),
        per_page=graphene.Int(20),
        search_tag=graphene.String(),
        created_with_in=graphene.Argument(CreatedWithIn),
        is_active=graphene.Boolean(),
    )
    all_suppliers = graphene.List(types.VendorType)
    all_subscription_plan = graphene.Field(types.AllVendorsubscriptionPlanType)

    vendor_expiration_status = graphene.Field(types.VendorExpirationStatusType)

    vendor_info = graphene.Field(
        types.VendorType, vendor_id=graphene.ID(), vendor_name=graphene.String()
    )
    get_vendor_document = graphene.List(types.VendorDocumentType)
    get_vendor_bankinfo = graphene.List(types.VendorBankType)

    convert_product_image_to_webp = graphene.Field(
        graphene.Boolean, delete_old_image=graphene.Boolean()
    )

    all_vendor_balance_log = graphene.Field(
        types.PaginatedVendorBlanceLogType,
        page=graphene.Int(1),
        per_page=graphene.Int(20),
    )
    all_vendor_balance_request = graphene.Field(
        types.PaginatedVendorBalanceWithdrawRequestType,
        page=graphene.Int(1),
        per_page=graphene.Int(20),
    )

    vendors_promotion = graphene.Field(
        types.VendorPromotionPaginatedType,
        page=graphene.Int(1),
        per_page=graphene.Int(20),
    )

    search_vendors = graphene.List(
        types.VendorType,
        search_tag=graphene.String(),
    )

    @permissions_checker([permissions.StaffPermission])
    def resolve_search_vendors(self, info, search_tag, **kwargs):
        return models.Vendor.objects.filter(
            Q(store_name__icontains=search_tag)
            | Q(email__icontains=search_tag)
            | Q(phone__icontains=search_tag)
            | Q(user__first_name__icontains=search_tag)
            | Q(user__last_name__icontains=search_tag)
        )[:10]

    
    def resolve_all_vendor_subscription_plans(self, info, **kwargs):
        return models.VendorsubscriptionPlan.objects.all()
    
 





    def create_thumbnail(kwargs, product):
        return_value = False
        im = Image.open(product.image.path)
        # 2. Converting the image to RGB colour:
        im = im.convert("RGBA")
        old_image_name = os.path.splitext(product.image.name)

        image_path = product.image.path
        split_tup = os.path.splitext(product.image.path)
        image_name = split_tup[0]
        image_extension = split_tup[1]

        print(im, "image", product.image, image_extension)
        if image_extension != ".webp":
            im.save(f"{image_name}.webp", "webp")
            product.image = f"{old_image_name[0]}.webp"
            product.save()
            if kwargs:
                os.remove(image_path)

                return_value = True
        im.close()

        return return_value

    # def create_thumbnail(size, path):

    # path = Path(path)
    # name = path.stem + '_thumbnail' + path.suffix
    # thumbnail_path = path.with_name(name)
    # image = Image.open(path)
    # image.thumbnail(size)
    # image.save(thumbnail_path)

    # def main():
    # ts = time()
    # Partially apply the create_thumbnail method, setting the size to 128x128
    # and returning a function of a single argument.
    # thumbnail_128 = partial(create_thumbnail, (128, 128))

    # Create the executor in a with block so shutdown is called when the block
    # is exited.
    # with ProcessPoolExecutor() as executor:
    # executor.map(thumbnail_128, Path('images').iterdir())
    # logging.info('Took %s', time() - ts)

    @classmethod
    def resolve_convert_product_image_to_webp(cls, root, info, **kwargs):

        # from PIL import Image
        products = core_ecommerce_models.Product.objects.all()
        thumbnail_128 = partial(cls.create_thumbnail, kwargs.get("delete_old_image"))
        # print(thumbnail_128,'thumbnail_128')
        with ProcessPoolExecutor() as executor:
            executor.map(thumbnail_128, list(products))
        # return_value = False
        # for product in products:
        #     if product.image:
        #         im = Image.open(product.image.path)
        #         # 2. Converting the image to RGB colour:
        #         im = im.convert('RGBA')
        #         old_image_name = os.path.splitext(product.image.name)

        #         # 3. Spliting the image path (to avoid the .jpg or .png being part of the image name):
        #         # image_name = image_path.split('.')[0]
        #         image_path = product.image.path
        #         split_tup = os.path.splitext(product.image.path)
        #         image_name = split_tup[0]
        #         image_extension = split_tup[1]

        #         print(im,'image',product.image,image_extension,image_name)

        #         if image_extension != '.webp' :
        #             im.save(f"{image_name}.webp", 'webp')
        #             product.image = f"{old_image_name[0]}.webp"
        #             product.save()
        #             if kwargs.get('delete_old_image'):
        #                 os.remove(image_path)

        #             return_value = True
        #         im.close()

        ProductImages = core_ecommerce_models.ProductImage.objects.all()
        thumbnail_128 = partial(cls.create_thumbnail, kwargs.get("delete_old_image"))
        # print(thumbnail_128,'thumbnail_128')
        with ProcessPoolExecutor() as executor:
            executor.map(thumbnail_128, list(ProductImages))
        return_value = False
        # for product in ProductImages:
        #     if product.image:
        #         im = Image.open(product.image.path)
        #         # 2. Converting the image to RGB colour:
        #         im = im.convert('RGBA')
        #         # pth =
        #         old_image_name = os.path.splitext(product.image.name)

        #         # 3. Spliting the image path (to avoid the .jpg or .png being part of the image name):
        #         # image_name = image_path.split('.')[0]
        #         image_path = product.image.path
        #         split_tup = os.path.splitext(product.image.path)
        #         image_name = split_tup[0]
        #         image_extension = split_tup[1]

        #         print(im,'image',product.image,image_extension)
        #         if image_extension != '.webp' :
        #             im.save(f"{image_name}.webp", 'webp')
        #             product.image = f"{old_image_name[0]}.webp"
        #             product.save()
        #             if kwargs.get('delete_old_image'):
        #                 os.remove(image_path)

        #             return_value = True

        #         im.close()
        # print(image_name,'image',image_extension,)
        return return_value

    @classmethod
    def resolve_vendor_info(cls, root, info, **kwargs):
        try:
            vendor_by_id = models.Vendor.objects.filter(id=kwargs.get("vendor_id"))
            vendor_count = models.VendorVisitorNumber.objects.filter(vendor=vendor_by_id.first()).first()
            if vendor_count == None:
                models.VendorVisitorNumber.objects.create(vendor=vendor_by_id,count=0)
            vendor_count.count += 1
            vendor_count.save()
            
        except:
            raise exceptions.GrapheneException("no vendor info")
        
        if vendor_by_id:
            return vendor_by_id.first()

        vendor_by_name = models.Vendor.objects.filter(
            store_name=kwargs.get("vendor_name")
        )

        if vendor_by_name:
            return vendor_by_name.first()
        return None

    @classmethod
    def resolve_all_subscription_plan(cls, root, info, **kwargs):
        from extra_settings.models import Setting

        value = Setting.get("VENDOR_SUBSCRIPTION_PLAN", None)
        if value:
            return {
                "basic": value.get("BASIC"),
                "gold": value.get("GOLD"),
                "standard": value.get("STANDARD"),
                "platinum": value.get("PLATINUM"),
            }
        return None

    # @permissions_checker([permissions.VendorsPermission])

    @classmethod
    def resolve_my_subscription_plan(cls, root, info, **kwargs):
        try:
            vendor = models.Vendor.objects.get(user_id=info.context.user.id)
            return models.Vendorsubscription.objects.filter(vendor=vendor).first()
        except models.Vendor.DoesNotExist:
            raise exceptions.GrapheneException("Vendor does not Exist")

    @classmethod
    def resolve_suppliers(cls, root, info, **kwargs):
        """
        @permission: None
        """
        return models.Vendor.objects.filter(user__user_role__is_supplier=True)

    @classmethod
    def resolve_supplier(cls, root, info, **kwargs):
        """
        @permission: None
        """
        try:
            return models.Vendor.objects.get(id=kwargs["id"])
        except models.Vendor.DoesNotExist:
            raise exceptions.GrapheneException(
                "The Vendor you are looking for does not existed"
            )

    @classmethod
    def resolve_retailers(cls, root, info, **kwargs):
        """
        @permission: None
        """
        return models.Vendor.objects.filter(user__user_role__is_retailer=True)

    @classmethod
    def resolve_retailer(cls, root, info, **kwargs):
        """
        @permission: None
        """
        try:
            return models.Vendor.objects.get(id=kwargs["id"])
        except models.Vendor.DoesNotExist:
            raise exceptions.GrapheneException(
                "The Vendor you are looking for does not existed"
            )

    @classmethod
    def resolve_get_detail_post(cls, root, info, **kwargs):
        """
        @return: Details of A Single Blog Post

        @permission: None
        """
        try:
            return models.Post.objects.get(id=kwargs["id"])
        except models.Post.DoesNotExist:
            raise exceptions.GrapheneException("Invalid post id")

    @permissions_checker([permissions.Authenticated])
    def resolve_get_footer(self, info, **kwargs):
        """
        @permission: Authenticated
        """
        return models.Footer.objects.all()

    @permissions_checker([permissions.Authenticated])
    def resolve_get_vendor_footer(self, info, **kwargs):
        """
        @permission: Authenticated
        """
        return models.VendorFooter.objects.all()

    @classmethod
    def resolve_get_vendor_followers(cls, root, info, **kwargs):
        """
        @return: followers users of a single vendor given id.

        @permission: None
        """
        return models.Follower.objects.filter(vendor_id=kwargs["vendor_id"])

    @permissions_checker([permissions.VendorsPermission])
    def resolve_vendor_dashboard_summery(self, info, **kwargs):
        """
        @return: all vendor data in short summery format.

        @permission: VendorPermission
        """
        vendor_user = info.context.user
        try:
            vendor = models.Vendor.objects.get(user=vendor_user)
        except models.Vendor.DoesNotExist:
            raise exceptions.GrapheneException("Vendor Not Found,")

        pending_orders = checkout_models.Order.objects.filter(
            product__vendor=vendor, checkoutorder__status="pending"
        )
        delivered_orders = checkout_models.Order.objects.filter(
            product__vendor=vendor, checkoutorder__status="completed"
        )
        canceled_orders = checkout_models.Order.objects.filter(
            product__vendor=vendor, checkoutorder__status="canceled"
        )
        accepted_orders = checkout_models.Order.objects.filter(
            product__vendor=vendor, checkoutorder__status="accepted"
        )

        sold_out_products = checkout_models.Order.objects.filter(
            product__vendor=vendor,
            checkoutorder__status="completed",
            checkoutorder__paid=True,
        )
        total_money = (
            sum(
                [(products.price - products.discount) for products in sold_out_products]
            )
            if sold_out_products
            else 0
        )
        total_tax = (
            sum([products.tax for products in sold_out_products])
            if sold_out_products
            else 0
        )
        top_5_products = list(sold_out_products)[:5]

        categories = core_ecommerce_models.Category.objects.all()
        products = core_ecommerce_models.Product.objects.filter(vendor=vendor)
        deleted_products = core_ecommerce_models.Product.objects.filter(is_active=False)
        promotions = models.Promotions.objects.all()

        return {
            "active_orders": accepted_orders.count(),
            "pending_orders": pending_orders.count(),
            "delivered_orders": delivered_orders.count(),
            "canceled_orders": canceled_orders.count(),
            "categories": categories.count(),
            "products": products.count(),
            "promotions": promotions.count(),
            "deleted_products": deleted_products.count(),
            "sold_out_products": sold_out_products,
            "total_money": total_money,
            "total_tax": total_tax,
            "top_5_products": top_5_products,
        }

    @permissions_checker([permissions.VendorsPermission])
    def resolve_inventory_management_summary(self, info, **kwargs):
        """
        @permission: VendorPermission
        """
        vendor_user = info.context.user
        all_details = []
        all_products = core_ecommerce_models.Product.objects.filter(
            vendor__user=vendor_user
        )
        for item in all_products:
            stock_amount = item.stock_amount
            # sold_amount=models.CheckoutOrder.objects.filter(ordered_from__user=vendor_user,product=item, order_status="completed").count()
            all_details.append(
                {
                    "stock_amount": stock_amount,
                    # 'sold_amount':sold_amount,
                    "item": item,
                }
            )
        return {"result": all_details}

    @permissions_checker([permissions.VendorsPermission])
    def resolve_vendor_data(self, info):
        """
        @return: currently authenticated vendor data

        @permission: VendorPermission
        """
        return models.Vendor.objects.get(user=info.context.user)

    # @permissions_checker([permissions.VendorsPermission])
    def resolve_vendor_gallery(self, info, **kwargs):
        """
        @return: return currently authenticated vendor pictures.

        @permission: VendorPermission
        """
        return models.VendorGallery.objects.filter(
            vendor__store_name=kwargs.get("store_name")
        )

    @classmethod
    def resolve_get_blog_post(cls, root, info, **kwargs):
        """
        @permission: None

        @return: all blog posts
        """
        return models.Post.objects.all()

    @classmethod
    def resolve_blogger_menu(cls, root, info, blogger_id):
        """
        @permission None

        @return: list of bloggerMenu objects given blogger ID.
        """
        return models.BloggerMenu.objects.filter(blogger_id=blogger_id)

    @permissions_checker([permissions.VendorsPermission])
    def resolve_vendor_social_link(self, info, **kwargs):
        """
        @permission: VendorPermission

        @return: All Social Media Links For A Specific Vendor
        """
        try:
            vendor = models.Vendor.objects.get(id=kwargs["vendor_id"])
        except models.Vendor.DoesNotExist:
            raise exceptions.GrapheneException("Vendor Not Found")
        return models.SocialLink.objects.filter(vendor=vendor).first()

  
    @classmethod
    def resolve_all_suppliers(cls, *args):
        """
        @permission: None

        @return: All Suppliers
        """
        return models.Vendor.objects.filter(is_supplier=True)

    @permissions_checker([permissions.VendorsPermission])
    def resolve_vendor_expiration_status(self, info):
        """
        @permission: VendorPermission

        @return: Vendor Registration Status
        """
        try:
            expiration = models.VendorRegistration.objects.get(
                vendor=info.context.user.vendor
            )
        except models.VendorRegistration.DoesNotExist:
            return None

        return {
            "expired": expiration.is_expired(),
            "days_left": expiration.days_left(),
            "registered_on": expiration.registered_on,
            "expires_on": expiration.expires_on,
        }

    @permissions_checker([permissions.VendorsPermission])
    def resolve_get_vendor_document(self, info, **kwargs):
        return models.VendorDocument.objects.filter(vendor=info.context.user.vendor)

    @permissions_checker([permissions.VendorsPermission])
    def resolve_get_vendor_bankinfo(self, info, **kwargs):
        return models.VendorBank.objects.filter(vendor=info.context.user.vendor)
