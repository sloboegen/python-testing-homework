from typing import Callable

import pytest
from typing_extensions import TypeAlias, TypeVar

_T = TypeVar('_T')
_ListEq: TypeAlias = Callable[[list[_T], list[_T]], None]


@pytest.fixture(scope='session')
def assert_list_eq() -> _ListEq[_T]:
    def _list_eq(xs: list[_T], ys: list[_T]) -> None:
        for x in xs:
            assert x in ys

        for y in ys:
            assert y in xs

    return _list_eq
