# Flexible API with GraphQL

In REST, you have a fixed set of endpoints. Want a user? `GET /users/1`. Want their posts? `GET /users/1/posts`. In GraphQL, there is only one endpoint — `/graphql`. The client sends a request in a special query language:

```graphql
query {
  user(id: 1) {
    name
    posts {
      title
    }
  }
}
```

And gets exactly what it asked for — not a byte more. That shifts control over the data from the server to the client.

## Key concepts

**Schema** — a strongly typed contract. It describes which data types exist and how they are related.

**Type** — a description of an object, for example `User` with fields like `id: ID!` and `name: String!`.

**Query** — the REST `GET` equivalent. It is the entry point for reading data.

**Mutation** — the REST `POST`/`PUT`/`DELETE` equivalent. It is the entry point for changing data.

**Resolver** — a piece of code that knows where to fetch the data for a specific field, whether from a database, an API, or a file.

## REST problems GraphQL solves

**Overfetching:** the server returns 50 fields, but the client only needs one. That wastes traffic.

**Underfetching:** to render a profile, the client needs 3 requests: for the user, their friends, and recent photos. In GraphQL, this can be one request.

## Client for graphQL

Endpoint: There is always just one, usually `/graphql`.  
Method: Always `POST` (rarely `GET`, when CDN caching is needed).  
Body: JSON in this form:

```json
{
  "query": "query($id: ID!) { user(id: $id) { name } }",
  "variables": { "id": 1 }
}
```

Variables: Never interpolate values directly into the query string with f-strings. That is dangerous because it can lead to injections, and it is inefficient because the server cannot cache the parsed query. Use `$variable` in the query and pass values separately in a dictionary.

## Implementation

```
servise2/
|
|- main.py (code)
|
|- schema.graphql (scheme of GraphQL)
|
|- client.py (requests)
````