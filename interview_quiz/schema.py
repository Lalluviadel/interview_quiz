import graphene
import api_graphene.schema
class Query(api_graphene.schema.Query, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass
class Mutation(api_graphene.schema.Mutation, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass
schema = graphene.Schema(query=Query, mutation=Mutation)
