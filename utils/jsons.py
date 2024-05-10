from uuid import UUID
from datetime import date, datetime
from itertools import chain


def to_dict(instance, fields=None):
    """
    Convert a model instance to a dictionary.

    :param instance: The model instance to convert.
    :param fields: A list of fields to include in the dictionary.
    :return: A dictionary representation of the model instance.
    """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        if fields and f.name not in fields:
            continue
        value = f.value_from_object(instance)

        if isinstance(value, UUID):
            value = value.hex
        if isinstance(value, (datetime, date)):
            value = value.isoformat()

        data[f.name] = value
    for f in opts.many_to_many:
        if fields and f.name not in fields:
            continue
        data[f.name] = [i.id.hex for i in f.value_from_object(instance)]
    return data
