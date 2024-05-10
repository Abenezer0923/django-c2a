from django.urls import path 

from . import views
urlpatterns = [
    # Other urlpatterns...
    path('create/', views.create_product, name='create_product'),
    path('success/', views.success, name='product_list'),
    # path('home/', views.home),
    
    
]
