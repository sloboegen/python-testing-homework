from typing import TYPE_CHECKING

import pytest
from django.test.client import Client
from django.urls import reverse

from server.apps.identity.models import User

if TYPE_CHECKING:
    from tests.plugins.http_helper import RedirectAssertion


@pytest.mark.django_db()
def test_logout(
    user: User,
    user_client: Client,
    assert_redirect: 'RedirectAssertion',
) -> None:
    response = user_client.post(
        reverse('identity:logout'),
    )

    assert_redirect(response, '/')
