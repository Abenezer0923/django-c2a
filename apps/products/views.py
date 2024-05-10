from django.shortcuts import render, redirect
from django.http import JsonResponse 
from graphene_django.views import GraphQLView
from .models import ProductsModel
from .forms import ProductForm 
from .models import ProductsModel       
def graphql_view(request):
    
    view = GraphQLView.as_view(graphiql=True)
    return view(request)

def show_product(request):
    # This view is just an example, replace it with your actual view logic
    # Here we're returning a simple JSON response
    products = [{'name': 'Product 1', 'price': 10}, {'name': 'Product 2', 'price': 20}]
    return JsonResponse({'products': products})
from .forms import ProductForm

def create_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product = product_form.save()
            return redirect('product_list')  # Redirect to the product list page after successful creation
    else:
        product_form = ProductForm()
    return render(request, 'products_form.html', {'product_form': product_form})

def success(request):
    return render(request, 'product_list.html')

def home(request):
    return render(request, 'product.html')

def show_products(request):
    products = ProductsModel.objects.all()
    return render(request, 'product_list.html', {'products': products})






