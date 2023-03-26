import random
from typing import Protocol, TypedDict, final

import pytest
from mimesis.providers.internet import Internet
from typing_extensions import Unpack


@final
class Picture(TypedDict, total=False):
    foreign_id: int
    url: str


class PictureFactory(Protocol):
    def __call__(self, **fields: Unpack[Picture]) -> Picture:
        """Picture factory protocol."""


@pytest.fixture()
def picture_factory() -> PictureFactory:
    def factory(**fields: Unpack[Picture]) -> Picture:
        return {
            'foreign_id': random.randint(a=1, b=100),
            'url': Internet().url(),
            **fields,  # type:ignore[misc]
        }

    return factory
