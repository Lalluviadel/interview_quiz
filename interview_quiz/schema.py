import graphene
import api_graphene.schema


class Query(api_graphene.schema.Query, graphene.ObjectType):
    pass


class Mutation(api_graphene.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
