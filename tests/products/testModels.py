import pytest
from apps.products.models import ProductsModel, Category, Colors

@pytest.mark.django_db

## Test for ProductsModel model
def test_product_creation():
    # Create necessary objects
    
    category = Category.objects.create(id=3, title="Test Category")
    color_blue, created = Colors.objects.get_or_create(name="blue")  

    
    product = ProductsModel.objects.create(
        product_id=223,
        product_name="Test Product",
        price=10,
        description="Test description",
        weight=1,
        review_count=0,
        category=category,
        slug="test-product_223",
        discount_percent=0,
        available_unit=15,
        product_img="test.png",
        rating=3,
    )
    product.color.add(color_blue)  # Asociation of color

    # Retrieve the saved product from the database
    saved_product = ProductsModel.objects.get(product_id=223)

    # Assertions
    assert saved_product.product_id == 223
    assert saved_product.product_name == "Test Product"
    assert saved_product.price == 10
    assert saved_product.description == "Test description"
    assert saved_product.weight == 1
    assert color_blue in saved_product.color.all()  
    assert saved_product.review_count == 0
    assert saved_product.category == category
    assert saved_product.slug == "test-product_223"
    assert saved_product.discount_percent == 0
    assert saved_product.available_unit == 15
    assert saved_product.product_img == "test.png"
    assert saved_product.rating == 3

## Test for Category Model 
@pytest.mark.django_db
def test_category_model():
    category = Category.objects.create(
      title = "Test Category", 
      keywords= " Test_keywords",
      description = "Test_description",
      image = "test.png", 
      slug = "test-category_123",
      status = "True",

    ) 
    save_category = Category.objects.get(slug="test-category_123")

    assert save_category.title == "Test Category"
    assert save_category.keywords == " Test_keywords"
    assert save_category.description == "Test_description"
    assert save_category.image == "test.png" 
    assert save_category.slug == "test-category_123"
    assert save_category.status == "True" 
