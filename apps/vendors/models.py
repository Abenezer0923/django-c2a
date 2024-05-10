from statistics import mode
from django.db import models
from apps.accounts.models import User
from utils.mixins import BaseModelMixin
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.contrib.postgres.fields import ArrayField
from dateutil.relativedelta import relativedelta
import datetime as dt
from datetime import datetime
from django.template.defaultfilters import slugify

from utils import fields


NULL = {"null": True, "blank": True}
null = {"null": True, "blank": True}


class Vendor(BaseModelMixin):
    """
    a single vendor (Retailer) object
    """

    user = models.OneToOneField(
        "accounts.User", on_delete=models.PROTECT, related_name="vendor"
    )
    store_name = models.CharField(max_length=255)
    description = models.TextField(**null)
    store_cover = models.ImageField(upload_to="store/image", **null)
    location = models.CharField(max_length=255, **null)
    store_locations = ArrayField(
        models.CharField(max_length=100, **NULL), **NULL)
    phone = models.CharField(max_length=255, **null)
    email = models.CharField(max_length=255, **null)
    video_url = models.URLField(max_length=255, **null)
    domain = models.URLField(**null)

    country = models.CharField(**null, max_length=50)
    region = models.CharField(**null, max_length=50)
    sub_city = models.CharField(**null, max_length=50)
    woreda = models.CharField(**null, max_length=50)
    kebele = models.CharField(**null, max_length=50)

    trade_licence = models.ImageField(upload_to="vendor_licence", **null)
    trade_name = models.CharField(max_length=255, **null)
    tin_number = models.CharField(max_length=100, **null)

    is_supplier = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_created_by",
    )
    updated_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_updated_by",
    )

    reference_code = models.CharField(**null, max_length=50)
    source_link = models.CharField(**null, max_length=50)

    support_phone = models.CharField(max_length=255, **null)
    support_email = models.CharField(max_length=255, **null)
    banner = models.ImageField(upload_to="banner/image", **null)
    logo = models.ImageField(upload_to="logo/image", **null)
    template_type = models.IntegerField(default=1)
    _store_type = [
        ("retailer", "Retailer"),
        ("wholesaler", "Wholesaler"),
        ("supplier", "Supplier"),
        ("manufacturer", "Manufacturer"),
        ("distributor", "Distributor"),
        ("big", "Big"),
        ("small", "Small"),
        ("medium", "Medium"),
    ]
    store_type = models.CharField(max_length=160, choices=_store_type, **NULL)

    catagories = ArrayField(models.CharField(max_length=100, **NULL), **NULL)
    support_phone_call = models.CharField(max_length=25, **null)

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        if not self.domain:
            self.domain = f"https://seller.purpose_black.com/{self.store_name}/"
        super().save(*args, **kwargs)

    @property
    def my_balance(self):
        return max(
            0,
            sum(
                [
                    vendorbalance.balance
                    for vendorbalance in self.vendorbalancelog_set.all()
                    if vendorbalance.balance_type == "DEPOSIT"
                ]
            )
            - sum(
                [
                    vendorbalance.balance
                    for vendorbalance in self.vendorbalancelog_set.all()
                    if vendorbalance.balance_type == "WITHDRAW"
                ]
            ),
        )


        if (
            self.vendorsubscription_set.exists()
            and self.vendorsubscription_set.first().end_date
            and self.vendorsubscription_set.first().end_date
            >= timezone.now().date()
            and self.vendorsubscription_set.first().paid
        ):
            return self.vendorsubscription_set.first()
        return self.vendorsubscription_set.first()

    @classmethod
    def is_vendor(cls, user_id):
        """
        check for a user for vendor status
        @param user_id: id of the user to check for vendor status
        @return: True if the user is vendor, False otherwise.
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return False

        try:
            cls.objects.get(user=user)
            return True
        except cls.DoesNotExist:
            return False
        
    @property
    def is_vendor_active(self):
        """
        check for vendor status
        @return: True if vendor is active, False otherwise.
        """
        return bool(self.products.all().count())

    def status(self) -> str:
        """
        @return: string formatted vendor status
        """
        registration = self.registration
        if registration.is_expired():
            return "EXPIRED"
        return "ON TRIAL"



class VendorPromotion(BaseModelMixin):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    end_date = models.DateField(null=False, blank=False)
    phone_number = models.CharField(max_length=15, null=False, blank=False)


class VendorAwards(BaseModelMixin):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="vendor/awards")
    title = models.TextField(**NULL)
    description = models.TextField(**NULL)

    created_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_award_created_by",
    )
    updated_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_award_updated_by",
    )


class VendorGallery(BaseModelMixin):
    """
    store multiple images for a single vendor
    """

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="vendor/gallery")
    img_desc = models.TextField(**null)

    created_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_gallary_created_by",
    )
    updated_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_gallary_updated_by",
    )


class VendorDocument(BaseModelMixin):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="vendor/document")
    title = models.TextField()
    description = models.TextField(**NULL)

    created_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_document_created_by",
    )
    updated_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_document_updated_by",
    )


class VendorBank(BaseModelMixin):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100, **NULL)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)
    account_type = models.CharField(max_length=100, **NULL)
    bank_branch = models.CharField(max_length=200, **NULL)

    created_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_bank_created_by",
    )
    updated_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_bank_updated_by",
    )


class VendorRegistration(BaseModelMixin):
    vendor = models.OneToOneField(
        Vendor, on_delete=models.CASCADE, related_name="registration"
    )
    registered_on = models.DateTimeField(default=timezone.localtime)
    expires_on = models.DateTimeField()

    def is_expired(self) -> bool:
        """
        check for vendor expiration status
        @return: bool: True if expired, False otherwise.
        """
        current = timezone.localtime()
        # 2022-11-11 - 2022-12-11
        diff_year = self.expires_on.year - current.year
        diff_month = self.expires_on.month - current.month
        diff_day = self.expires_on.day - current.day

        if diff_year < 0:
            return True
        if diff_year <= 0 and diff_month < 0:
            return True
        if diff_year <= 0 and diff_month < 0 and diff_day < 0:
            return True
        return False

    def days_left(self):
        # TODO: resolve this method
        return 14


class SocialLink(BaseModelMixin):
    """
    All Social Media Links For A Single Vendor
    """

    vendor = models.OneToOneField(
        Vendor, models.CASCADE, related_name="social_links")
    facebook       = models.URLField(**null)
    telegram       = models.URLField(**null)
    youtube        = models.URLField(**null)
    tiktok         = models.URLField(**null)
    website_url    = models.URLField(**null)


    created_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="social_created_by",
    )
    updated_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="social_updated_by",
    )


class Promotions(BaseModelMixin):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="promotions", **null)
    size = models.CharField(max_length=255)
    label = models.CharField(max_length=255)

    def __str__(self):
        return str(self.pk)


class Post(BaseModelMixin):
    """
    a blog post having all contents of a post
    """

    author = models.ForeignKey("accounts.User", models.CASCADE)
    title = models.CharField(max_length=255)
    type_of_post = models.TextField(**null)
    content = models.TextField()
    image = models.ImageField(**null, upload_to="blog-post-img/")
    video = models.FileField(**null, upload_to="blog-post-vid/")

    def __str__(self):
        return self.title


class BloggerMenu(BaseModelMixin):
    blogger = models.ForeignKey("accounts.User", models.CASCADE)
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(**null)


class VendorFooter(BaseModelMixin):
    vendor = models.OneToOneField(Vendor, models.CASCADE)
    our_service = models.JSONField(default=dict)
    trade_service = models.JSONField(default=dict)
    our_products = models.JSONField(default=dict)
    who_we_are = models.JSONField(default=dict)


class Footer(BaseModelMixin):
    our_courses = models.JSONField(default=dict)
    about = models.JSONField(default=dict)
    our_ecommerce = models.JSONField(default=dict)
    make_money = models.JSONField(default=dict)

    created_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="footer_created_by",
    )
    updated_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="footer_updated_by",
    )


class Follower(BaseModelMixin):
    """
    vendors followers, unique vendor and user relation
    """

    vendor = models.ForeignKey(Vendor, models.CASCADE)
    user = models.ForeignKey("accounts.User", models.CASCADE)

    created_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_follower_created_by",
    )
    updated_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_follower_updated_by",
    )

    class Meta:
        unique_together = (
            "vendor",
            "user",
        )

    def __str__(self):
        return f"{self.user.username} following {self.vendor.user.username}"


class VendorInvitation(BaseModelMixin):
    email = models.EmailField()
    name = models.CharField(max_length=100)

    created_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_invi_created_by",
    )
    updated_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_invi_updated_by",
    )

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs):
        message = EmailMessage(
            "Ashewa Invitation",
            get_template(
                "vendors/invitation.html").render({"name": self.name}),
            "Ashewa Sells Team",
            [self.email],
        )
        message.content_subtype = "html"
        # message.send()
        super().save(*args, **kwargs)


class VendorBalanceLog(BaseModelMixin):
    """
    Vendor Blance Log model
    """

    vendor = models.ForeignKey(Vendor, models.CASCADE)
    _type = [
        ("DEPOSIT", "DEPOSIT"),
        ("WITHDRAW", "WITHDRAW"),
        ("FREE_DELIVERY", "FREE_DELIVERY"),

    ]
    balance_type = models.CharField(
        max_length=60,
        choices=_type,
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    updated_by = models.ForeignKey(
        "accounts.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_review_updated_by",
    )


class VendorBalanceWithdrawRequest(BaseModelMixin):
    """
    Vendor Balance Withdraw Request
    """

    vendor = models.ForeignKey(Vendor, models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    _status = [
        ("PENDING", "PENDING"),
        ("APPROVED", "APPROVED"),
        ("CANCELED", "CANCELED"),
        ("CASHED_OUT", "CASHED_OUT"),
    ]
    status = models.CharField(
        max_length=60, choices=_status, default="PENDING")
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        **NULL,
        related_name="request_approved_by",
    )
    approved_on = models.DateTimeField(blank=True, null=True)
    cashed_out_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        **NULL,
        related_name="request_cashed_out",
    )
    cashed_out_on = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class VendorPromotionSubscription(BaseModelMixin):
    """
    Vendor Promotion Subscription
    """

    vendor = models.ForeignKey(Vendor, models.CASCADE)
    phone_number = models.CharField(max_length=20)
    _status = [
        ("APPROVED", "APPROVED"),
        ("CANCELED", "CANCELED"),
    ]
    status = models.CharField(
        max_length=60, choices=_status, default="PENDING")
    active_until = models.IntegerField(blank=True, null=True)
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        **NULL,
        related_name="promotion_approved_by",
    )
    approved_on = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)



class VendorVisitorNumber(BaseModelMixin):
    vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)
    count  = models.IntegerField(default=0)

    def __str__(self):
        return f" vendor id {self.vendor.id} is visited {self.count} times"


