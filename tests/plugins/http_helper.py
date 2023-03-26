from http import HTTPStatus
from typing import Callable

import django.http
import pytest
from typing_extensions import TypeAlias

RedirectAssertion: TypeAlias = Callable[[django.http.HttpResponse, str], None]


@pytest.fixture()
def assert_redirect() -> RedirectAssertion:
    def _checker(response: django.http.HttpResponse, redirect_to: str) -> None:
        assert response.status_code == HTTPStatus.FOUND
        assert response.get('Location') == redirect_to

    return _checker
