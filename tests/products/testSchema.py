import pytest
import requests

# GraphQL URL
GRAPHQL_URL = "http://localhost:8000/graphql/"
@pytest.fixture
def graphql_client():
  def _graphql_client(query):
    headers = {"Content-Type": "application/json"}
    response = requests.post(GRAPHQL_URL, headers=headers, json={"query": query})
    if response.status_code != 200:
      raise Exception(f"GraphQL request failed with status code: {response.status_code}")
    return response
  return _graphql_client


def test_query_all_products(graphql_client):
    # GraphQL query for fetching all products
    query = """
    query AllProducts{
  allProducts{
    price
    productId
    productName
    category{
      slug
      status
      description
      title
      parent{
        id
        title
        
      }
    }
  }
}
    """

    
    response = graphql_client(query)

    # Assert the response contains the expected data
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "errors" not in data
    products = data["data"]["allProducts"]
    assert isinstance(products, list)
    

## Test for create product

def test_mutation_create_product(graphql_client):
    
    mutation = """
    mutation CreateProduct {
      createProduct(
        productId: 591233
        productImg: null
        rating: 3
        productName: "Water Bottle"
        price: 32
        description: "a water bottle made from plastic"
        weight: 2
        color: "black"
        reviewCount: 2
        categoryId: 2
        slug: "product_bottle_4aq5as1521"
        discountPercent: 5
      ) {
        products {
          productName
          productId
          category {
            title
            parent {
              id
              title
            }
          }
        }
      }
    }
    """

    # Send the mutation to the GraphQL server
    response = graphql_client(mutation)

    # Assert the response contains the expected data
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "errors" not in data
    products = data["data"]["createProduct"]["products"]  # Corrected field name to 'products'
    assert products is not None
    assert isinstance(products, dict)
    
## Test for update product    
def test_mutation_update_product(graphql_client):
    # Define the GraphQL mutation for creating a product
    mutation = """
    mutation UpdateProduct {
      updateProduct(
        productId: 563
        productImg: null
        rating: 3
        productName: "Electric Stove"
        price: 32
        description: "electric stove made up of copper and silver"
        weight: 2
        color: "blue"
        reviewCount: 2
        categoryId: 2
        
        discountPercent: 5
      ) {
        products {
          productName
          productId
          category {
            title
            parent {
              id
              title
            }
          }
        }
      }
    }
    """

    # Send the mutation to the GraphQL server
    response = graphql_client(mutation)

    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "errors" not in data
    products = data["data"]["updateProduct"]["products"]  
    assert products is not None
    assert isinstance(products, dict)


## Test for delete product
def test_mutation_delete_product(graphql_client):
   mutation = """
      mutation DeleteProduct{
        deleteProduct(productId: 34){
            success
        }
    }
              """

   response = graphql_client(mutation)

   assert response.status_code == 200
   data = response.json()
   assert "data" in data 
   assert "errors" not in data
   success = data["data"]["deleteProduct"]["success"]
   assert success is True
   assert isinstance(success, bool)

