from django.db import models
from django.utils import timezone
from django.contrib import admin
from tinymce.widgets import TinyMCE
import graphene
from uuid import uuid4
from . import methods
# from graphql.language.ast import BooleanValue, FloatValue, IntValue, StringValue
import json
from django.utils.html import escape
from django.core.exceptions import ValidationError

NULL = {"null": True, "blank": True}


class ModelAdminMixin(admin.ModelAdmin):
    exclude = ["created_at", "updated_at", "created_by", "updated_by"]
    formfield_overrides = {
        models.TextField: {"widget": TinyMCE()},
    }
    search_fields = ("user__username",)

class PaginatedTypeMixin(graphene.ObjectType):
    """
    parent class for paginating objects

    child must override the objects field with graphene.List(ChildObjectType)
    """

    page = graphene.Int()  # required result paginated page
    pages = graphene.Int()  # number of total pages
    # True if there is a next page relative to current page
    has_next = graphene.Boolean()
    # True if there is a previous page relative to current page
    has_prev = graphene.Boolean()
    # child must override this field with graphene.List(ChildObjectType)
    objects = None
    total_objects = graphene.Int()  # number of total objects from all pages
    


class ImageScalar(graphene.String):
    @staticmethod
    def parse_literal(ast):
        if isinstance(ast, StringValue):
            return methods.base64_to_object(ast.value)
        
    @staticmethod
    def parse_value(ast):
        value = "".join(ast.split(',')[1:]) if ast.count(",") > 0 else ast 
        return methods.base64_to_object(value)
class BaseModelMixin(models.Model):
    """
    Base Parent Model Mixin That Wraps All Common Fields and methods.
    child can override any of the methods or fields.
    """

    id = models.UUIDField(
        default=uuid4, primary_key=True, editable=False, db_index=True
    )

    created_at = models.DateTimeField(default=timezone.localtime)
    updated_at = models.DateTimeField(**NULL)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.updated_at = timezone.localtime()
            self.clean_fields
        for f in self._meta.fields:
            raw_value = getattr(self, f.attname)
            if f.blank and raw_value in f.empty_values:
                continue
            elif type(raw_value) == str:
                try:
                    setattr(self, f.attname, escape(raw_value))
                except ValidationError as e:
                    pass
        super().save(*args, **kwargs)

