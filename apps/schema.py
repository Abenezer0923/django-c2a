import graphene
import graphql_jwt


from apps.accounts import (
    mutations as account_mutations,
    models as accounts_models,
    schema as accounts_schema,
    types as accounts_type,
)

from apps.vendors import (
    mutations as vendor_mutations,
    schema as vendors_schema,
)



from graphql_jwt import utils
from graphene.types.generic import GenericScalar


class Query(
    accounts_schema.Query,
    vendors_schema.Query,
   
):
    pass


class VerifyTokenType(graphene.ObjectType):
    user = graphene.Field(accounts_type.UserType)
    extra = GenericScalar()


class VerifyToken(graphene.Mutation):
    class Arguments:
        token = graphene.String()

    payload = graphene.Field(VerifyTokenType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        _payload = utils.get_payload(kwargs["token"])
        data = {
            "user": accounts_models.User.objects.get(username=_payload["username"]),
            "extra": _payload,
        }
        return VerifyToken(data)

class Mutations(
    account_mutations.Mutation,
    vendor_mutations.Mutation,
):
    verify_token = VerifyToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutations)
