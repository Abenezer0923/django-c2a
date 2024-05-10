from django.contrib import admin
from . import models
from utils.mixins import ModelAdminMixin
import csv
from django.http import HttpResponse



def export_to_excel(self,request,queryset):
    vendors = models.Vendor.objects.all()
    meta = self.model._meta
    field_names = [field.name for field in meta.fields]
    field_names = field_names[1:]


    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in vendors:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response


class VendorAdmin(ModelAdminMixin):
    list_display =  ["store_name", "is_supplier", "domain", "status", "domain"]
    search_fields = ["store_name"]
    list_filter = ["is_supplier"]
    exclude = ["domain"]
    # actions = [export_to_excel]


class VendorRegistrationAdmin(ModelAdminMixin):
    list_display = ["vendor", "registered_on", "expires_on", "is_expired"]
    actions = ['export_to_excel']

class VendorPromotionAdmin(ModelAdminMixin):
    list_display = ["vendor", "end_date", "phone_number",]
    actions = ['export_to_excel']

admin.site.register(models.VendorVisitorNumber)
admin.site.register(models.Vendor, VendorAdmin)
admin.site.register(models.VendorGallery, ModelAdminMixin)
admin.site.register(models.SocialLink, ModelAdminMixin)
admin.site.register(models.Promotions, ModelAdminMixin)
admin.site.register(models.Footer, ModelAdminMixin)
admin.site.register(models.VendorFooter, ModelAdminMixin)
admin.site.register(models.Follower, ModelAdminMixin)
admin.site.register(models.Post, ModelAdminMixin)
admin.site.register(models.BloggerMenu, ModelAdminMixin)
admin.site.register(models.VendorRegistration, VendorRegistrationAdmin)
admin.site.register(models.VendorInvitation)


admin.site.register(models.VendorBalanceWithdrawRequest)




admin.site.register(models.VendorBank, ModelAdminMixin)
admin.site.register(models.VendorDocument, ModelAdminMixin)
admin.site.register(models.VendorPromotion, VendorPromotionAdmin)
admin.site.register(models.VendorPromotionSubscription)






