from django.contrib import admin
from django.urls import path, include, include
from django.conf import settings
from django.conf.urls.static import static
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from graphql_jwt.decorators import jwt_cookie
from graphql_playground.views import GraphQLPlaygroundView
# from graphql.error.located_error import GraphQLLocatedError
from decouple import config
from django.urls import re_path


class _GraphQLView(GraphQLView,):

    @staticmethod
    def format_error(error):
        try:
            _error = {
                "message": error.original_error.context.get("message"),
                "status": error.original_error.context.get("status"),
            }
        except AttributeError:
            try:
                _error = {"message": error.message, "status": 400}
            except Exception as e:
                # TODO: Handle this exception
                print(f"exception in graphql exception class: {e}")
                _error = {"message": error.__str__(), "status": 400}

        return _error


urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/',include('apps.products.urls')),
    path("graphql/", csrf_exempt(jwt_cookie(_GraphQLView.as_view(graphiql=True)))),
    path("playground/", GraphQLPlaygroundView.as_view(endpoint="/graphql/")),
]
