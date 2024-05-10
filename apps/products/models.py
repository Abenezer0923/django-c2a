from django.db import models 
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator 
from django.utils.text import slugify
from django.db.utils import IntegrityError
from django.urls import reverse
from .validators import size_validator
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

ProductColors = (
    ('black', 'Black'),
    ('white', 'White'),
    ('gray', 'Gray'),
    ('red', 'Red'),
    ('blue', 'Blue'),
    ('green', 'Green'),
    ('yellow', 'Yellow'),
    ('orange', 'Orange'),
    ('purple', 'Purple'),
    ('pink', 'Pink'),
    ('brown', 'Brown'),
    ('beige', 'Beige'),
    ('navy', 'Navy'),
    ('teal', 'Teal'),
    ('burgundy', 'Burgundy'),
)

class Colors(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True, choices=ProductColors, verbose_name='Product Color')

    def __str__(self):
        return self.name
class Category(MPTTModel):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )

    parent = TreeForeignKey('self', on_delete= models.CASCADE, related_name='children', null=True, blank=True)
    title = models.CharField(max_length=250)
    keywords = models.CharField(max_length= 250)
    description = models.TextField()
    image = models.ImageField(upload_to='products/category/',validators=[FileExtensionValidator(['png','jpg']), size_validator] )
    slug = models.SlugField(null=False, unique=True)
    status=models.CharField(max_length=10, choices=STATUS)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    def __save__(self, *args, **kwargs):
        self.slug_counter = 11
        if not self.slug:
            self.slug = slugify(f"{self.title}_{self.slug_counter}")
        while True:
            try:
                super(Category, self).save(*args, **kwargs)
                return
            except IntegrityError: 
                
                self.slug = f"{self.slug}_{self.slug_counter}"
                self.slug_counter += 1




    class MPTTMeta:
        order_insertion_by = ['title']

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    def __str__(self):                           
        full_path = [self.title]                  
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' / '.join(full_path[::-1])


        

class ProductsModel(models.Model):
    product_name = models.CharField(max_length=256)
    product_id = models.AutoField(primary_key=True)
         ### Future 
    # vendor = models.ForeignKey(VendorModel, on_delete=models.CASCADE)
    
    price = models.IntegerField(verbose_name='Price', default=0)
    description = models.TextField(max_length=6000, null=False, blank=False, verbose_name='Description')
    discount_percent = models.IntegerField(blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)] )
    available_unit = models.IntegerField(verbose_name='Available Unit', null=True, blank=True)
    review_count = models.IntegerField(verbose_name='Reviews', blank=True, validators=[MinValueValidator(0) ,MaxValueValidator(5)])
    color = models.ManyToManyField(Colors, blank=True)
    product_img = models.ImageField(default=None,  upload_to='product_image/', validators=[FileExtensionValidator(['png','jpg']), size_validator])
    weight = models.IntegerField(verbose_name='Product Weight', null=True, blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True, blank=True)
    rating = models.IntegerField(verbose_name='Rating', null=True, blank=True)
    category= models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)

    class Meta:
        db_table = 'products_productsmodel'
    
     
    def __str__(self):
        return self.product_name


