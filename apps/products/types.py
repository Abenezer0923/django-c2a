# types.py
from graphene_django import DjangoObjectType
import graphene
from graphene_file_upload.scalars import Upload
from .models import ProductsModel, Category, Colors

class ColorsType(DjangoObjectType):
    class Meta:
        model = Colors
        
class CategoryType(DjangoObjectType):
    class Meta:
        model= Category
        fields = ('id','parent','title', 'keywords', 'description', 'image', 'slug', 'status')


class ProductsType(DjangoObjectType):

    class Meta:
        model = ProductsModel
        fields = ('product_name', 'product_id', 'price', 'product_img', 'description', 'available_unit' , 'discount_percent', 
                  'available_unit', 'review_count', 'color', 'weight', 'date_created', 'date_updated', 'rating', 'category', 'slug')
        colors = graphene.Field(Colors)