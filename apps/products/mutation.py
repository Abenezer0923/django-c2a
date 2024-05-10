import graphene
from graphene_file_upload.scalars import Upload
from django.utils.text import slugify
from django.db.utils import IntegrityError
from .models import Category, ProductsModel, Colors
from .types import CategoryType, ProductsType

class CreateProduct(graphene.Mutation):
    class Arguments:
        
        product_name = graphene.String()
        product_img = Upload()
        price = graphene.Float()
        description = graphene.String()
        discount_percent = graphene.Int()
        available_unit = graphene.Int()
        weight = graphene.Int()
        rating = graphene.Int()
        review_count = graphene.Int()
        date_created = graphene.Date()
        date_updated = graphene.Date()
        slug = graphene.String()
        category_id = graphene.ID()
        colors = graphene.List(graphene.String)

    products = graphene.Field(ProductsType)

    @classmethod
    def mutate(cls, root, info, product_name, product_img=None, price=None, description=None,
               discount_percent=None, available_unit=None,  weight=None,
               rating=None, review_count=None, date_created=None, date_updated=None,
               slug=None, category_id=None, colors=None):
        
        product_category = Category.objects.get(id=category_id)
        base_slug = slugify(f"{product_category.title}_{product_name}")
        slug_counter = 1
        slug = f"{base_slug}_{slug_counter}" 
        while ProductsModel.objects.filter(slug=slug).exists():
            slug_counter += 1
            slug = f"{base_slug}_{slug_counter}"

        product = ProductsModel.objects.create(
            product_name=product_name,
            product_img=product_img,
            price=price,
            description=description,
            discount_percent=discount_percent,
            available_unit=available_unit,
            weight=weight,
            rating=rating,
            review_count=review_count,
            date_updated=date_updated,
            date_created=date_created,
            slug=slug,
            category_id=category_id,
            
        )

        if colors:
            color_objects = Colors.objects.filter(name__in=colors)
            if len(color_objects) != len(colors):
                raise IntegrityError("Cannot find all the requested color names!")
            product.color.set(color_objects)      
                   
        
        return CreateProduct(products=product)

class UpdateProduct(graphene.Mutation):
    class Arguments:
        product_id = graphene.ID(required=True)
        product_name = graphene.String()
        product_img = Upload()
        price = graphene.Float()
        description = graphene.String()
        discount_percent = graphene.Int()
        available_unit = graphene.Int()
        weight = graphene.Int()
        rating = graphene.Int()
        review_count = graphene.Int()
        date_created = graphene.Date()
        date_updated = graphene.Date()
        slug = graphene.String()
        category_id = graphene.ID()
        colors = graphene.List(graphene.String)

    products = graphene.Field(ProductsType)

    @classmethod
    def mutate(cls, root, info, product_id, product_name=None, product_img=None, price=None,
               description=None, discount_percent=None, available_unit=None, colors=None,
               weight=None, rating=None, review_count=None, slug=None,
               date_updated=None, category_id=None):
        
        
        try:
            product = ProductsModel.objects.get(product_id=product_id)
        except ProductsModel.DoesNotExist:
            raise Exception("Product with id {} does not exist".format(product_id))

        if product_name is not None:
            product.product_name = product_name
        if product_img is not None:
            product.product_img = product_img
        if price is not None:
            product.price = price
        if description is not None:
            product.description = description
        if discount_percent is not None:
            product.discount_percent = discount_percent
        if available_unit is not None:
            product.available_unit= available_unit
        if weight is not None:
            product.weight = weight
        if rating is not None:
            product.rating = rating 
        if review_count is not None:
            product.review_count= review_count
        if date_updated is not None:
            product.date_updated = date_updated  
        if slug is not None:
            product.slug = slug       
        if category_id is not None:
            product.category_id = category_id
        if colors:
            color_objects = Colors.objects.filter(name__in=colors)
            if len(color_objects) != len(colors):
                raise IntegrityError("Cannot find all the requested color names!")
            product.color.set(color_objects)     

        product.save()
        return UpdateProduct(products=product)

class DeleteProduct(graphene.Mutation):
    class Arguments:
        product_id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, product_id):
        try:
            product = ProductsModel.objects.get(product_id=product_id)
        except ProductsModel.DoesNotExist:
            raise Exception("Product with id {} does not exist".format(product_id))

        product.delete()
        return DeleteProduct(success=True)

class CreateCategory(graphene.Mutation):
    class Arguments:
        parent = graphene.ID(required=False)
        title = graphene.String()
        keywords = graphene.String()
        description = graphene.String()
        image = Upload()
        status = graphene.String()
        slug = graphene.String()

    category_input = graphene.Field(CategoryType)

    @classmethod
    def mutate(cls, root, info, title=None, keywords=None, parent=None, description=None, image=None,
               slug=None, status=None):
        
        parent_category = None
        if parent:
            parent_category = Category.objects.get(id=parent)
        
        slug_counter = 1
        base_slug = slugify(title)
        slug = f"{base_slug}_{slug_counter}"
        if Category.objects.filter(slug=slug).exists():
            slug_counter +=1
            slug = f"{base_slug}_{slug_counter}"


        category = Category.objects.create(
            title=title,
            keywords=keywords,
            description=description,
            image=image,
            slug=slug,
            status=status,
            parent= parent_category,
        )
        return CreateCategory(category_input=category)

# Define queries
class Query(graphene.ObjectType):
    all_products = graphene.List(ProductsType)
    all_categories = graphene.List(CategoryType)
    product_by_id = graphene.Field(ProductsType, product_id=graphene.ID())
    category_by_id = graphene.Field(CategoryType, category_id=graphene.ID())

    def resolve_all_products(root, info):
        return ProductsModel.objects.all()

    def resolve_all_categories(root, info):
        return Category.objects.all()

    def resolve_product_by_id(root, info, product_id):
        return ProductsModel.objects.get(pk=product_id)

    def resolve_category_by_id(root, info, category_id):
        return Category.objects.get(pk=category_id)

# Define mutations
class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    create_category = CreateCategory.Field()