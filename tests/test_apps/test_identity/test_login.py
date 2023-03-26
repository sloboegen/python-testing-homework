from http import HTTPStatus
from typing import TYPE_CHECKING

import django.http
import pytest
from django.test.client import Client
from django.urls import reverse

from server.apps.identity.models import User

if TYPE_CHECKING:
    from tests.plugins.http_helper import RedirectAssertion
    from tests.plugins.identity.user import RegistrationData, UserDataPassword


def _login_request(client: Client, username: str, password: str) -> django.http.HttpResponse:
    return client.post(
        reverse('identity:login'),
        data={
            'username': username,
            'password': password,
        }
    )


@pytest.mark.django_db()
def test_success_login(
    client: Client,
    user_data: 'UserDataPassword',
    assert_redirect: 'RedirectAssertion',
) -> None:
    """This test ensures that registered user can successfully log in."""
    response = _login_request(
        client,
        username=user_data['email'],
        password=user_data['password'],
    )

    assert_redirect(response, reverse('pictures:dashboard'))


@pytest.mark.django_db()
def test_login_already_logged_in(
    user: User,
    user_client: Client,
    assert_redirect: 'RedirectAssertion',
) -> None:
    """This test ensures that log in for already logged-in user redirects to dashboard."""
    response = _login_request(
        user_client,
        username='',
        password=''
    )

    assert_redirect(response, reverse('pictures:dashboard'))


@pytest.mark.django_db()
@pytest.mark.parametrize('password', ['', '#!', 'incorrect', '1' * 100])
def test_login_incorrect_password(
    client: Client,
    user_data: 'UserDataPassword',
    password: str
) -> None:
    """This test ensures that user must provide correct email and password."""
    response = _login_request(
        client,
        username=user_data['email'],
        password=password
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_login_unknown_user(
    client: Client,
    registration_data: 'RegistrationData',
) -> None:
    """This test ensures that unregistered user can not log in."""
    response = _login_request(
        client,
        username=registration_data['email'],
        password=registration_data['password1'],
    )

    assert response.status_code == HTTPStatus.OK
