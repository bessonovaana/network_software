import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional
import uvicorn
import random


comments_db= {}

@strawberry.type
class Comment:
    id: str
    author: str
    text: str

@strawberry.type
class Query:
    @strawberry.field
    def comment(self, id: str) -> Optional[Comment]:
        return comments_db.get(id)
    @strawberry.field()
    def comments(self) -> List[Comment]:
        return list(comments_db.values())
    
@strawberry.type()
class Mutation:
    @strawberry.mutation
    def createComment(self, author: str, text: str) -> Comment:
        count=int(random.randint(1,100))
        new_id = str(count)
        comment = Comment(
            id =new_id,
            author = author,
            text =text
        )
        comments_db[new_id]=comment
        return comment

schema = strawberry.Schema(query =Query, mutation = Mutation)
app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
    
  