from django.utils.text import slugify
from graphql.language.ast import BooleanValue, FloatValue, IntValue, StringValue
from graphene.types import Scalar
from django.utils.html import escape
import re
# import phonenumbers


pattern_list = []


def validate(value):

    try:
        for i in range(len(pattern_list) + 1):
            if pattern_list[i].match(value):
                break
    except IndexError as e:
        raise ValueError(f"'{value}' is invalid") from e


class Initializer(Scalar):
    def __init__(self, *args, **kwargs):
        if validate := kwargs.pop("validate", None):
            pattern = re.compile(validate)
            if pattern not in pattern_list:
                pattern_list.append(pattern)
        super().__init__(*args, **kwargs)

    @staticmethod
    def serialize_parse(value):
        validate(value)
        if isinstance(value, bool):
            return "true" if value else "false"
        return value or None

    serialize = serialize_parse
    parse_value = serialize_parse

    @staticmethod
    def parse_literal(node):
        "if value is GraphQL literal, this method receives it"

        validate(node.value)
        values = (StringValue, IntValue, FloatValue, BooleanValue)
        return node.value if isinstance(node, values) else None


class Stringy(Initializer):
    """Custom string scalar"""


class Inty(Initializer):
    """Custom int scalar"""


class Floaty(Initializer):
    """Custom float scalar"""


class Booly(Initializer):
    """Custom boolean scalar"""

    serialize = bool
    parse_value = bool


class Idy(Initializer):
    """Custom ID scalar"""


def escape_str(kwargs):

    _kwargs = {}
    for k, w in kwargs.items():
        if type(w) == str:
            _kwargs[k] = escape(w)
        else:
            _kwargs[k] = w
    return _kwargs


def is_valid_phone_number(number: str, country_code: int = 0)-> bool:
        """
        Returns True if the given string represents a valid international phone number
        in the E.164 format, False otherwise.
        """
        # phone_number = f'+{country_code}{number}'
        # try:
        #     return phonenumbers.is_valid_number_for_region(phonenumbers.parse(
        #         phone_number), phonenumbers.region_code_for_country_code(country_code))
        # except phonenumbers.phonenumberutil.NumberParseException:
        #     return False

        pattern = re.compile(r'^\+(?:[0-9]?){6,14}[0-9]$')
        return bool(pattern.match(number))
    
def is_markdown_string(text:str)-> bool:
    # define the regular expression to match markdown syntax
    markdown_regex = r'^#.*|(?<=\s)_(\S.*?\S|\S)_|\*\*(\S.*?\S|\S)\*\*|\[(.*?)\]\((.*?)\)|```(.|\n)*?```|(!\[.*?\]\((.*?)\))|(\|.*?)+\|?\s*\n?-+\|(.+\|)+|\n(> .*|\*\s.+\n)+|(- \[[x ]\] .+\n)+|\*{3}(.+)?\*{3}|\_{3}(.+)?\_{3}'

    # use the re.search() function to search for the pattern in the text
    if re.search(markdown_regex, text):
        return True
    else:
        return False


def amharic_slugify(text):
    # Replace any non-letter or non-digit characters with a space
    text = re.sub(r'[^\w\s]', ' ', text)
    # Replace any whitespace with a hyphen
    text = re.sub(r'\s+', '-', text)
    # Convert to lowercase
    text = text.lower()
    # Return the resulting slug
    return text

def django_slugify(value):
    # Use Django's default slugify function for ASCII characters
    slug = slugify(value)
    # Use our custom Amharic slugify function for non-ASCII characters
    if not all(ord(c) < 128 for c in value):
        amharic_slug = amharic_slugify(value)
        slug = slug if amharic_slug == '' else amharic_slug
    return slug
