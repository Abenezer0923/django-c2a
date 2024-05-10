# query.py
import graphene
from .types import  ProductsType, CategoryType
from .models import ProductsModel, Category 


class Query(graphene.ObjectType):

    Get_product = graphene.List(ProductsType, product_id=graphene.ID())
    get_category = graphene.List(CategoryType, category=graphene.String())
    all_products = graphene.List(ProductsType)
    all_category = graphene.List(CategoryType)
    all_main_categories = graphene.List(CategoryType)
    all_sub_categories = graphene.List(CategoryType)
    subcategories_by_main_category = graphene.List(CategoryType, main_category_id=graphene.ID())

    def resolve_subcategories_by_main_category(root, info, main_category_id):
        try:
            category = Category.objects.get(pk=main_category_id)
            return Category.objects.filter(parent=category)
        except:
            Category.DoesNotExist
            return None
        


    def resolve_all_main_categories(root, info):
        return Category.objects.filter(parent__isnull=True)
    def resolve_all_sub_categories(root, info):
        return Category.objects.exclude(parent__isnull=True)
    def resolve_all_products(root, info):
        return ProductsModel.objects.all()

    def resolve_all_category(root, info):
        return Category.objects.all()
 
    def resolve_Get_product(root, info, product_id):
        if product_id:
            return ProductsModel.objects.filter(product_id=product_id)
        else:
            return ProductsModel.objects.all()

    def resolve_get_category(self, info, category):
        categories = Category.objects.filter(title=category)
        return list(categories)