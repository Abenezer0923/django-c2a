from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django import forms
from django.db.models import Sum, Value
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models
from django.db.models import Sum
from django.contrib.admin import SimpleListFilter
from django.contrib.admin import DateFieldListFilter
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import csv
from django.http import HttpResponse

class UserCreationForm(forms.ModelForm):
    """
    Modified User Creation Form For Admin Panel
    """

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = models.User
        fields = ("email",)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        try:
            validate_password(password2)
        except ValidationError as e:
            raise forms.ValidationError(" ".join(e))
        
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    Django's Modified User Update Admin Form
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = models.User
        fields = "__all__"

    def clean_password(self):
        return self.initial["password"]

def export_to_excel(self,request,queryset):
    
    # orders = models.CheckoutOrder.objects.all()
    users = models.User.objects.all()
    meta = users.model._meta
    field_names = [field.name for field in meta.fields]
    field_names = field_names[1:]
  
  


    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in users:
        row = [getattr(obj, field) for field in field_names]
        row = writer.writerow(row)
    return response


class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = (
        "username",
        "first_name",
        "last_name",
        "phone",
        "is_staff",
        "is_active",
        "role",
      
       
    )
    actions = [export_to_excel]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "age",
                    "gender",
                    "phone",
                    "is_staff",
                    "password",
                    "role",
                )
            },
        ),
        ("Personal info", {"fields": ["profile_pic"]}),
        ("Permissions", {"fields": ("is_superuser",
         "is_verified", "is_active", "groups")}),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = (
        "first_name",
        "last_name",
        "phone",
        "username",
        "role",
    )
    ordering = (
        "first_name",
        "last_name",
    )
    filter_horizontal = ()







class PointFilter(SimpleListFilter):
    title = 'points'
    parameter_name = 'points'

    def lookups(self, request, model_admin):
        return (
            ('more', ('More than 2000')),
            ('less', ('Less than 2000')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'more':
            return queryset.filter(won_points__gte=2000)
        elif self.value() == 'less':
            return queryset.filter(won_points__lte=2000)



admin.site.register(models.User, CustomUserAdmin)
admin.site.register(models.ResetCode)

