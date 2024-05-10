from django.core.exceptions import ValidationError # type: ignore

def size_validator(value):
    max_size = 5242880  # 5MB in bytes

    if value.size > max_size:
        raise ValidationError('File should not exceed more than 5MB')