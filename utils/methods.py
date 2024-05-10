import io
import graphene
import random
import string
import base64
import time
from django.db.models.query_utils import DeferredAttribute
from django.db.models.fields.related_descriptors import (
    ForeignKeyDeferredAttribute,
    ForwardOneToOneDescriptor,
    ForwardManyToOneDescriptor,
)
from django.db.models.fields.files import ImageFileDescriptor
from django.core.files.images import ImageFile
from PIL import Image



def get_graphene_string_field(length: 1):
    return [graphene.String() for _ in range(length)]


def checkout_reference():
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(5)
    )


def reset_code():
    return "".join(random.choice(string.digits) for _ in range(6))


def coupon_code():
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(8)
    )


def get_model_field(model: object) -> list:
    all_fields = model.__dict__
    fields = []

    types = [
        DeferredAttribute,
        ForeignKeyDeferredAttribute,
        ForwardOneToOneDescriptor,
        ForwardManyToOneDescriptor,
        ImageFileDescriptor,
    ]

    for field, obj_type in all_fields.items():
        if type(obj_type) in types and "_id" not in field:
            fields.append(field)

    return fields + ["id"]


def base64_to_object(b64_img=None) -> ImageFile or None:
    if not b64_img:
        return None
    image = Image.open(io.BytesIO(base64.b64decode(b64_img)))
    thumb_bytes = io.BytesIO()
    image.save(thumb_bytes, format="webp", optimize = True, quality = 40)
    return ImageFile(thumb_bytes,name=f"{time.time().__int__()}.webp")