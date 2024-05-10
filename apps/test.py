import pytest
from graphene.test import Client
from .schema import schema

@pytest.fixture
def graphql_client():
    return Client(schema)

def test_user_signup_mutation(graphql_client):
    mutation = '''
        mutation UserSignup($input: UserSignupInput!) {
            userSignup(input: $input) {
                payload {
                    id
                    username
                    first_name
                    last_name
                }
                token
            }
        }
    '''

    variables = {
        'input': {
            'username': 'testuser',
            'password': 'testpassword',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890',
            'email': 'testuser@example.com',
            'is_buyer': True
        }
    }

    # Execute the mutation
    result = graphql_client.execute(mutation, variables=variables)

    # Check if the mutation was successful
    assert 'errors' not in result

    # Check the returned payload and token
    payload = result['data']['userSignup']['payload']
    assert payload['username'] == 'testuser'
    assert payload['first_name'] == 'John'
    assert payload['last_name'] == 'Doe'

    token = result['data']['userSignup']['token']
    assert token is not None