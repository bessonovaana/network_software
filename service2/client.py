import requests


URL = "http://localhost:8000/graphql"

project_code = "tickets-s04"
def build_payload(query: str, variables: dict) -> dict:
    """
    Формирует словарь для отправки GraphQL запроса.

    :param query: Текст запроса (query или mutation).
    :param variables: Словарь с переменными.
    :return: Словарь с ключами "query" и "variables".
    """
    return {
        "query": query,
        "variables": variables,
    }


def send_graphql_request(query: str, variables: dict) -> dict:
    payload = build_payload(query, variables)
    response = requests.post(URL, json=payload)
    response.raise_for_status()
    return response.json()


def print_result(result: dict) -> None:
    if "errors" in result and result["errors"]:
        print("Errors:")
        for error in result["errors"]:
            print(error)
    if "data" in result and result["data"] is not None:
        print("Data:")
        print(result["data"])


def main() -> None:
    query_comments = """
    query {
      comments {
        id
        author
        text
      }
    }
    """

    result = send_graphql_request(query_comments, {})
    print_result(result)

    mutation_create_comment = """
    mutation CreateComment($author: String!, $text: String!) {
      createComment(author: $author, text: $text) {
        id
        author
        text
      }
    }
    """

    variables = {
        "author": "lol",
        "text": "Hhehe"
    }

    result = send_graphql_request(mutation_create_comment, variables)
    print_result(result)


if __name__ == "__main__":
    main()