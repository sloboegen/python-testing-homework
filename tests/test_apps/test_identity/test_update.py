from typing import TYPE_CHECKING

import pytest
from django.test.client import Client
from django.urls import reverse

from server.apps.identity.models import User

if TYPE_CHECKING:
    from tests.plugins.http_helper import RedirectAssertion
    from tests.plugins.identity.user import RegistrationDataFactory


def test_update_for_logged_in_only(
    client: Client,
    assert_redirect: 'RedirectAssertion',
) -> None:
    """This test ensures that `/identity/update` can use only logged in users."""

    response = client.post(
        reverse('identity:user_update'),
    )

    assert_redirect(response, '/identity/login?next=/identity/update')


@pytest.mark.django_db()
@pytest.mark.parametrize('modified_field', User.REQUIRED_FIELDS)
def test_update_fields(
    user: User,
    user_client: Client,
    registration_data_factory: 'RegistrationDataFactory',
    modified_field: str,
    assert_redirect: 'RedirectAssertion',
) -> None:
    """This test ensures that updating user info is correct."""
    new_user_data = registration_data_factory()

    response = user_client.post(
        reverse('identity:user_update'),
        data=new_user_data,
    )

    modified_user = User.objects.filter(email=user.email).first()
    assert getattr(modified_user, modified_field) == new_user_data[modified_field]

    assert_redirect(response, reverse('identity:user_update'))
