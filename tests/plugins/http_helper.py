from http import HTTPStatus
from typing import Callable, Any

import pytest
from typing_extensions import TypeAlias

RedirectAssertion: TypeAlias = Callable[[Any, str], None]


# NOTE: I have not found type for django response...

@pytest.fixture()
def assert_redirect() -> RedirectAssertion:
    def _checker(response: Any, redirect_to: str) -> None:
        assert response.status_code == HTTPStatus.FOUND
        assert response.get('Location') == redirect_to

    return _checker
