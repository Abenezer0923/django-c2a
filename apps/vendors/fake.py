import factory
from .models import Vendor

class VendorFactory(factory.DjangoModelFactory):
    class Meta:
        model = Vendor

    user        = factory.Faker("user")
    store_name  = factory.Faker("company")
    description  = factory.Faker("user")
    store_cover = factory.Faker("company")
    location   = factory.Faker("company")
    store_locations = factory.Faker("company")
    phone = factory.Faker("phone")
    email = factory.Faker("email")
    
    