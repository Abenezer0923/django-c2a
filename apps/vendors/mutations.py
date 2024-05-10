from datetime import datetime, timezone
import graphene
from django_graphene_permissions import permissions_checker

# from js2py import require
from apps.accounts.models import User
from . import models, types
from utils import permissions, exceptions, mixins, methods
from .models import VendorBalanceLog




class UpdateVendorStoreLocationsMutation(graphene.Mutation):
    """
    update existing vendor store_locations.

    @permission: VendorPermission.
    """

    class Arguments:
        store_locations = graphene.List(graphene.String)

    payload = graphene.Field(types.VendorType)

    @permissions_checker([permissions.VendorsPermission, permissions.Authenticated])
    def mutate(self, info, **kwargs):
        try:
            store = models.Vendor.objects.get(user=info.context.user)
        except models.Vendor.DoesNotExist:
            raise exceptions.GrapheneException("vendor not found")

        store_locations = [
            store_location
            for store_location in store.store_locations
            if not kwargs.get("store_locations").__contains__(store_location)
        ]
        store.store_locations = store_locations

        store.save()

        return UpdateVendorStoreLocationsMutation(store)


class UpdateVendorCatagoriesMutation(graphene.Mutation):
    """
    update existing vendor catagories.

    @permission: VendorPermission.
    """

    class Arguments:
        catagories = graphene.List(graphene.String)

    payload = graphene.Field(types.VendorType)

    @permissions_checker([permissions.VendorsPermission, permissions.Authenticated])
    def mutate(self, info, **kwargs):
        try:
            store = models.Vendor.objects.get(user=info.context.user)
        except models.Vendor.DoesNotExist:
            raise exceptions.GrapheneException("vendor not found")

        catagories = [
            catagory
            for catagory in store.catagories
            if not kwargs.get("catagories").__contains__(catagory)
        ]
        store.catagories = catagories

        if not store.permited_action("add_category"):
            raise exceptions.GrapheneException(
                "Upgrade your subscription to get this feature!")

        store.save()

        return UpdateVendorCatagoriesMutation(store)


class UpdateVendorMutation(graphene.Mutation):
    """
    update existing vendor data.

    @permission: VendorPermission.
    """

    class Arguments:
        (
            store_name,
            description,
            phone,
            email,
            video_url,
            location,
            support_email,
            support_phone,
            support_phone_call,
        ) = [graphene.String() for _ in range(9)]
        store_cover, trade_licence, banner, logo = [
            mixins.ImageScalar() for _ in range(4)
        ]
        country, region, sub_city, woreda, kebele = [
            graphene.String() for _ in range(5)
        ]
        tin_number, trade_name = [graphene.String() for _ in range(2)]
        reference_code, source_link = [graphene.String() for _ in range(2)]
        catagories = graphene.List(graphene.String)
        store_locations = graphene.List(graphene.String)
        template_type = graphene.Int(1)
        is_active = graphene.Boolean()
        vendor_id = graphene.UUID()

    payload = graphene.Field(types.VendorType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        if info.context.user.is_superuser and kwargs.get("vendor_id"):
            store = models.Vendor.objects.get(id=kwargs.get("vendor_id"))
        else:
            store = models.Vendor.objects.get(user=info.context.user)
        store.store_name = kwargs.get("store_name") or store.store_name
        store.description = kwargs.get("description") or store.description
        store.phone = kwargs.get("phone") or store.phone
        store.email = kwargs.get("email") or store.email
        store.video_url = kwargs.get("video_url") or store.video_url
        store.location = kwargs.get("location") or store.location
        store.store_cover = kwargs.get("store_cover") or store.store_cover

        store.trade_licence = kwargs.get(
            "trade_licence") or store.trade_licence
        store.tin_number = kwargs.get("tin_number") or store.tin_number

        store.country = kwargs.get("country") or store.country
        store.region = kwargs.get("region") or store.region
        store.sub_city = kwargs.get("sub_city") or store.sub_city
        store.woreda = kwargs.get("woreda") or store.woreda
        store.kebele = kwargs.get("kebele") or store.kebele
        store.trade_name = kwargs.get("trade_name") or store.trade_name

        store.reference_code = kwargs.get(
            "reference_code") or store.reference_code
        store.source_link = kwargs.get("source_link") or store.source_link

        store.reference_code = kwargs.get(
            "reference_code") or store.reference_code
        store.source_link = kwargs.get("source_link") or store.source_link

        store.support_phone = kwargs.get(
            "support_phone") or store.support_phone
        store.support_email = kwargs.get(
            "support_email") or store.support_email
        store.banner = kwargs.get("banner") or store.banner
        if kwargs.get("logo") and not store.permited_action("add_business_logo"):
            raise exceptions.GrapheneException(
                "Upgrade your subscription to get this feature!")
        else:
            store.logo = kwargs.get("logo") or store.logo
        store.catagories = kwargs.get("catagories") or store.catagories
        store.store_locations = kwargs.get(
            "store_locations") or store.store_locations
        store.template_type = kwargs.get(
            "template_type") or store.template_type
        store.support_phone_call = kwargs.get(
            "support_phone_call") or store.support_phone_call

        try:
            store.is_active = kwargs.pop("is_active")
        except:
            pass

        store.save()

        return UpdateVendorMutation(store)


class CreateUpdateVendorSocialLinkMutation(graphene.Mutation):
    """
    create vendors social media links, update if exists.

    @permission: VendorPermission.
    """

    class Arguments:
        facebook, telegram, youtube,tiktok,website_url = [graphene.String() for _ in range(5)]

    payload = graphene.Field(types.SocialLinkType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        vendor = info.context.user.vendor

        try:
            social_link = vendor.social_links
            social_link.facebook = (
                kwargs.get("facebook")
                if kwargs.get("facebook") is not None
                else social_link.facebook
            )
            social_link.telegram = (
                kwargs.get("telegram")
                if kwargs.get("telegram") is not None
                else social_link.telegram
            )
            social_link.youtube = (
                kwargs.get("youtube")
                if kwargs.get("youtube") is not None
                else social_link.youtube
            )
            subcribed = None
            try:
                subcribed = models.Vendorsubscription.objects.get(id = vendor.id)

            except models.Vendorsubscription.DoesNotExist:
                exceptions.GrapheneException("No subcribed user")

            if subcribed:
                social_link.tiktok = (
                    kwargs.get("tiktok")
                    if kwargs.get("tiktok") is not None
                    else social_link.tiktok
                )
                social_link.website_url = (
                    kwargs.get("website_url")
                    if kwargs.get("website_url") is not None
                    else social_link.website_url
                )

            social_link.save()
        except models.Vendor.social_links.RelatedObjectDoesNotExist:
            social_link = models.SocialLink.objects.create(
                vendor=vendor, **kwargs)

        return CreateUpdateVendorSocialLinkMutation(social_link)


class CreateVendorMutation(graphene.Mutation):
    """
    create a new vendor on specific tenant
    """

    class Arguments:
        user = graphene.UUID(required=True)
        (
            store_name,
            description,
            phone,
            email,
            video_url,
            location,
            support_email,
            support_phone,
        ) = [graphene.String() for _ in range(8)]
        store_cover, trade_licence, banner, logo = [
            mixins.ImageScalar() for _ in range(4)
        ]

        country, region, sub_city, woreda, kebele = [
            graphene.String() for _ in range(5)
        ]
        tin_number, trade_name = [graphene.String() for _ in range(2)]
        reference_code, source_link = [graphene.String() for _ in range(2)]
        catagories = graphene.List(graphene.String)
        store_locations = graphene.List(graphene.String)
        template_type = graphene.Int(1)

    payload = graphene.Field(types.VendorType)

    @classmethod
    def mutate(cls, *args, **kwargs):
        user_id = kwargs.pop("user")

        try:
            models.Vendor.objects.get(user_id=user_id)
            raise exceptions.GrapheneException("Vendor Already Exist")
        except models.Vendor.DoesNotExist:
            phone = kwargs.get("phone")
            if phone:
                kwargs.pop("phone")
            else:
                phone = User.objects.get(id=user_id).phone
            vendor = models.Vendor.objects.create(
                user_id=user_id,
                phone=phone,
                **kwargs,
            )
            if kwargs.get("logo") and not vendor.permited_action("add_business_logo"):
                vendor.log = None
                vendor.save()
            return CreateVendorMutation(vendor)


class AddVendorImage(graphene.Mutation):
    """
    vendors gallery (multiple image for a vendor)
    """

    class Arguments:
        # vendor_id = graphene.UUID(required=True)
        image = mixins.ImageScalar(required=True)
        img_desc = graphene.String()

    payload = graphene.Field(types.VendorGalleryType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        if not info.context.user.vendor.permited_action("add_business_logo"):
            raise exceptions.GrapheneException(
                "Upgrade your subscription to get this feature!")

        obj = models.VendorGallery.objects.create(
            vendor=info.context.user.vendor, **kwargs
        )
        return AddVendorImage(obj)


class DeleteVendorImage(graphene.Mutation):
    class Arguments:
        image_id = graphene.ID(required=True)

    deleted = graphene.Boolean()

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        try:
            image = models.VendorGallery.objects.get(id=kwargs["image_id"])
            image.delete()
            return DeleteVendorImage(True)
        except models.VendorGallery.DoesNotExist:
            return DeleteVendorImage(False)


class AddVendorPromotion(graphene.Mutation):
    """
    pass
    """

    class Arguments:
        image = mixins.ImageScalar(required=True)
        size, label = [graphene.String(required=True) for _ in range(2)]

    payload = graphene.Field(types.PromotionType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        obj = models.Promotions.objects.create(
            vendor=models.Vendor.objects.get(user=info.context.user),
            image=kwargs["image"],
            size=kwargs["size"],
            label=kwargs["label"],
        )
        return AddVendorPromotion(obj)


class VerifyVendorMutation(graphene.Mutation):
    """
    check if a user is a vendor
    """

    class Arguments:
        user_id = graphene.UUID(required=True)

    payload = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        return VerifyVendorMutation(models.Vendor.is_vendor(kwargs["user_id"]))


class VerifyVendorIdMutation(graphene.Mutation):
    """
    @deprecated, this mutation class has been already created, its duplicated
    """

    class Arguments:
        user_id = graphene.UUID(required=True)

    payload = graphene.Field(types.VendorType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            vendor = models.Vendor.objects.get(user_id=kwargs["user_id"])
            return VerifyVendorIdMutation(vendor)
        except models.Vendor.DoesNotExist:
            raise exceptions.GrapheneException("Vendor Doesnt Exist")


class VendorFollow(graphene.Mutation):
    class Arguments:
        user_id, vendor_id = [graphene.UUID(required=True) for _ in range(2)]

    payload = graphene.Field(types.FollowerType)

    @permissions_checker([permissions.Authenticated])
    def mutate(self, info, **kwargs):
        try:
            user = User.objects.get(id=kwargs["user_id"])
        except User.DoesNotExist:
            raise exceptions.GrapheneException("user not found")

        try:
            vendor = models.Vendor.objects.get(id=kwargs["vendor_id"])
        except models.Vendor.DoesNotExist:
            raise exceptions.GrapheneException("vendor not found")

        try:
            follower = models.Follower.objects.get(vendor=vendor, user=user)
        except models.Follower.DoesNotExist:
            follower = models.Follower.objects.create(vendor=vendor, user=user)

        return VendorFollow(follower)


class VendorFooterMutator(graphene.Mutation):
    class Arguments:
        vendor = graphene.UUID(required=True)
        our_courses, about, our_ecommerce, make_money = [
            graphene.JSONString() for _ in range(4)
        ]

    payload = graphene.Field(types.FooterType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        vendor = models.Vendor.objects.filter(id=kwargs["vendor_id"])
        if not vendor:
            raise exceptions.GrapheneException("Vendor Not Found")

        try:
            footer = models.VendorFooter.objects.get(vendor=vendor.first())
        except models.VendorFooter.DoesNotExist:
            footer = models.VendorFooter.objects.create(vendor=vendor.first())

        if kwargs.get("our_service"):
            footer.our_service = {**footer.our_service,
                                  **kwargs.get("our_service")}
        if kwargs.get("about"):
            footer.our_service = {**footer.about, **kwargs.get("about")}
        if kwargs.get("our_ecommerce"):
            footer.our_service = {**footer.our_ecommerce,
                                  **kwargs.get("our_ecommerce")}
        if kwargs.get("make_money"):
            footer.our_service = {
                **footer.make_money, **kwargs.get("make_money")}


class LegalDocuments(graphene.InputObjectType):
    image = mixins.ImageScalar(required=True)
    title = graphene.String(required=True)
    description = graphene.String()


class AddListVendorLegalDoument(graphene.Mutation):
    class Arguments:
        vendor_id = graphene.ID(required=True)
        legal_documents = graphene.List(LegalDocuments, required=True)

    payload = graphene.List(types.VendorDocumentType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        legal_documents = []
        try:
            vendor = models.Vendor.objects.get(id=kwargs.pop("vendor_id"))
        except models.Vendor.DoesNotExist:
            raise exceptions.GrapheneException("Vendor does not exist")

        for legal_document in kwargs.get("legal_documents"):
            doc = models.VendorDocument.objects.create(
                vendor=vendor,
                image=legal_document.image,
                title=legal_document.title,
                description=legal_document.description,
            )
            legal_documents.append(doc)
        return AddListVendorLegalDoument(legal_documents)


class AddVendorDoument(graphene.Mutation):
    class Arguments:
        vendor_id = graphene.ID(required=True)
        image = mixins.ImageScalar(required=True)
        title = graphene.String(required=True)
        description = graphene.String()

    payload = graphene.Field(types.VendorDocumentType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        return AddVendorDoument(models.VendorDocument.objects.create(**kwargs))


class EditVendorDoument(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        image = mixins.ImageScalar()
        title = graphene.String()
        description = graphene.String()

    payload = graphene.Field(types.VendorDocumentType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        try:
            doc: models.VendorDocument = models.VendorDocument.objects.get(
                id=kwargs.get("id")
            )
        except models.VendorDocument.DoesNotExist:
            raise exceptions.GrapheneException("Document Not Found")

        doc.image = kwargs.get("image") or doc.image
        doc.title = kwargs.get("title") or doc.title
        doc.description = kwargs.get("description") or doc.description

        doc.save()

        return AddVendorDoument(doc)


class AddVendorAwards(graphene.Mutation):
    class Arguments:
        vendor_id = graphene.ID(required=True)
        awards = graphene.List(LegalDocuments, required=True)

    payload = graphene.List(types.VendorAwardType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        awards = []
        try:
            vendor = models.Vendor.objects.get(id=kwargs.pop("vendor_id"))
        except models.Vendor.DoesNotExist:
            raise exceptions.GrapheneException("Vendor does not exist")

        for award in kwargs.get("awards"):
            doc = models.VendorAwards.objects.create(
                vendor=vendor,
                image=award.image,
                title=award.title,
                description=award.description,
            )
            awards.append(doc)
        return AddVendorAwards(awards)




class AddVendorVisitorCount(graphene.Mutation):

    """ 
        Number of visiting client is always increase when this mutation called from front end
    """
    
    class Arguments:
        vendor_id = graphene.ID(required=True)
    payload = graphene.Field(types.VendorVisitorNumberType)
    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        vendor_id = kwargs.pop("vendor_id")
        vendor_count = models.VendorVisitorNumber.objects.filter(vendor=vendor_id).first()
        if vendor_count == None:
            try:
                vendor = models.Vendor.objects.get(id = vendor_id)

            except models.Vendor.DoesNotExist:
                raise exceptions.GrapheneException("Vendor does't exist")
            vendor_count = models.VendorVisitorNumber.objects.create(vendor= vendor,count = 0)
        vendor_count.count += 1
        vendor_count.save()
        return AddVendorVisitorCount(vendor_count)




class EditVendorAward(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        image = mixins.ImageScalar()
        title = graphene.String()
        description = graphene.String()

    payload = graphene.Field(types.VendorAwardType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        try:
            doc: models.VendorAwards = models.VendorAwards.objects.get(
                id=kwargs.get("id")
            )
        except models.VendorAwards.DoesNotExist:
            raise exceptions.GrapheneException("Awards Not Found")

        doc.image = kwargs.get("image") or doc.image
        doc.title = kwargs.get("title") or doc.title
        doc.description = kwargs.get("description") or doc.description

        doc.save()

        return EditVendorAward(doc)


class DeleteVendorAwardMutation(graphene.Mutation):
    class Arguments:
        document_id = graphene.ID(required=True)

    deleted = graphene.Boolean()

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        try:
            document = models.VendorAwards.objects.get(
                id=kwargs["document_id"])
            document.delete()
            return DeleteVendorAwardMutation(True)
        except models.VendorAwards.DoesNotExist:
            return DeleteVendorAwardMutation(False)


class DeleteVendorDocumentMutation(graphene.Mutation):
    class Arguments:
        document_id = graphene.ID(required=True)

    deleted = graphene.Boolean()

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        try:
            document = models.VendorDocument.objects.get(
                id=kwargs["document_id"])
            document.delete()
            return DeleteVendorDocumentMutation(True)
        except models.VendorDocument.DoesNotExist:
            return DeleteVendorDocumentMutation(False)


class AddVendorBankInfo(graphene.Mutation):
    class Arguments:
        bank_name, account_name, account_number = [
            graphene.String(required=True) for _ in range(3)
        ]
        bank_branch, account_type = [graphene.String() for _ in range(2)]
        vendor_id = graphene.ID(required=True)

    payload = graphene.Field(types.VendorBankType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        return AddVendorBankInfo(
            models.VendorBank.objects.create(
                vendor=info.context.user.vendor, **kwargs)
        )


class EditVendorBankInfo(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        bank_name, account_name, account_number, account_type, bank_branch = [
            graphene.String() for _ in range(5)
        ]

    payload = graphene.Field(types.VendorBankType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):

        try:
            bank_info: models.VendorBank = models.VendorBank.objects.get(
                id=kwargs["id"]
            )
        except models.VendorBank.DoesNotExist:
            raise exceptions.GrapheneException("Bank Info Not Found!")

        bank_info.bank_name = kwargs.get("bank_name") or bank_info.bank_name
        bank_info.account_name = kwargs.get(
            "account_name") or bank_info.account_name
        bank_info.account_number = (
            kwargs.get("account_number") or bank_info.account_number
        )
        bank_info.account_type = kwargs.get(
            "account_type") or bank_info.account_type
        bank_info.bank_branch = kwargs.get(
            "bank_branch") or bank_info.bank_branch

        bank_info.save()

        return AddVendorBankInfo(bank_info)


class DeleteVendorBankInfo(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    deleted = graphene.Boolean()

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        try:
            bank = models.VendorBank.objects.get(id=kwargs["id"])
            bank.delete()
            return DeleteVendorBankInfo(True)
        except models.VendorBank.DoesNotExist:
            return DeleteVendorBankInfo(False)


class VendorBalanceWithdrawRequestMutation(graphene.Mutation):
    class Arguments:
        balance = graphene.Decimal(required=True)

    withdraw_request = graphene.Field(types.VendorBalanceWithdrawRequestType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
        if kwargs["balance"] > info.context.user.vendor.my_balance:
            raise exceptions.GrapheneException(
                "you dont have Balance to withdraw")
            return VendorBalanceWithdrawRequestMutation(None)
        withdraw_request = models.VendorBalanceWithdrawRequest.objects.create(
            vendor=info.context.user.vendor, **kwargs
        )
        return VendorBalanceWithdrawRequestMutation(withdraw_request)
    
    
    

class VendorStroreFrontMutation(graphene.Mutation):
    class Arguments:
        id               = graphene.ID(required=True)
        theme            = mixins.ImageScalar()
        bannerUrl        = graphene.String()
        featuredProducts = graphene.List(graphene.UUID)

    vendor_store_front = graphene.Field(types.VendorStoreFrontType)

    @permissions_checker([permissions.VendorsPermission])
    def mutate(self, info, **kwargs):
       
        vendor_store_front = models.VendorStoreFront.objects.create(
            vendor=info.context.user.vendor, **kwargs
        )
        return VendorStroreFrontMutation(vendor_store_front)







class Mutation(graphene.ObjectType):
    create_vendor = CreateVendorMutation.Field()
    update_vendor = UpdateVendorMutation.Field()
    store_front_vendor_store = VendorStroreFrontMutation.Field()
    add_vendor_image = AddVendorImage.Field()
    delete_vendor_image = DeleteVendorImage.Field()
  
    vendor_store_front = VendorStroreFrontMutation.Field()




















































































































