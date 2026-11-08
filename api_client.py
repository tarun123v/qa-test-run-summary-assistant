import json
from urllib.error import HTTPError
from urllib.request import urlopen


def fetch_post(post_id: int) -> dict[str, object]:
    """Fetch a post and return only its ID, title, and body."""
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"

    try:
        with urlopen(url, timeout=10) as response:
            if not 200 <= response.status < 300:
                raise RuntimeError(
                    f"Request failed with HTTP status {response.status}: {response.reason}"
                )

            post = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise RuntimeError(
            f"Request failed with HTTP status {error.code}: {error.reason}"
        ) from error

    if not isinstance(post, dict):
        raise ValueError("The API response was not a JSON object.")

    required_fields = ("id", "title", "body")
    if any(field not in post for field in required_fields):
        raise ValueError("The API response is missing id, title, or body.")

    return {field: post[field] for field in required_fields}
