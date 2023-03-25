from http import HTTPStatus
from typing import TYPE_CHECKING, Protocol, TypedDict, final, Callable
from typing_extensions import Unpack, TypeAlias

import pytest
from django.test.client import Client
from django.urls import reverse
from mimesis.providers.person import Person

from server.apps.identity.models import User

if TYPE_CHECKING:
    from tests.plugins.identity.user import RegistrationData


@final
class LoginData(TypedDict):
    username: str
    password: str


class LoginDataFactory(Protocol):
    def __call__(self, **fields: Unpack[LoginData]) -> LoginData:
        """Login data factory protocol."""


@pytest.fixture()
def login_data_registered_factory(user: User) -> LoginDataFactory:
    def factory(**fields: Unpack[LoginData]) -> LoginData:
        return {
            'username': user.email,
            'password': user.password,
            **fields,
        }

    return factory


@pytest.fixture()
def login_data_unknown_factory(user: User) -> LoginDataFactory:
    def factory(**fields: Unpack[LoginData]) -> LoginData:
        provider = Person()
        return {
            'username': provider.email(),
            'password': provider.password(),
            **fields,
        }

    return factory


@pytest.mark.django_db()
def test_success_login(
    client: Client,
    login_data_registered_factory: LoginDataFactory,
) -> None:
    """This test ensures that registered user can successfully log in."""
    login_data = login_data_registered_factory()

    response = client.post(
        reverse('identity:login'),
        data=login_data,
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('pictures:dashboard')

# @pytest.mark.django_db()
# def test_failed_login_missing_fields(
#     client: Client,
#     login
# ) -> None:
#     """This test ensures that user can not log in without providing email and password."""
#     pass


# @pytest.mark.django_db()
# def test_failed_login_unknown_user(
#     client: Client,
#     login_data_unknown: LoginData,
# ) -> None:
#     """This test ensures that unknown user can not log in."""
#
#     response = client.post(
#         reverse('identity:login'),
#         data=login_data_registered,
#     )
#
#     assert response.status_code == HTTPStatus.FOUND
#     assert response.get('Location') == reverse('pictures:dashboard')
