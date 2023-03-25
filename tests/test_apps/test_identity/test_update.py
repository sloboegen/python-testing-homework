from http import HTTPStatus

from django.test.client import Client
from django.urls import reverse


def test_update_for_logged_in_only(
    client: Client,
) -> None:
    """This test ensures that `/identity/update` can use only logged in users."""

    response = client.post(
        reverse('identity:user_update'),
        data={}
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == '/identity/login?next=/identity/update'
