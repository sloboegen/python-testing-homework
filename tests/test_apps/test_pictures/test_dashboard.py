from collections.abc import Iterable
from typing import TYPE_CHECKING, Callable, TypeVar

import pytest
from django.test.client import Client
from django.urls import reverse
from typing_extensions import TypeAlias

from server.apps.identity.models import User
from server.apps.pictures.logic.repo.queries import favourite_pictures
from server.apps.pictures.models import FavouritePicture

if TYPE_CHECKING:
    from tests.plugins.pictures.picture import Picture, PictureFactory

_T = TypeVar('_T')
_ListEq: TypeAlias = Callable[[list[_T], list[_T]], bool]


@pytest.fixture()
def _list_eq() -> _ListEq:
    def __list_eq(xs: list[_T], ys: list[_T]) -> bool:
        f = True
        for x in xs:
            f &= x in ys

        for y in ys:
            f &= y in xs

        return f

    return __list_eq


def _convert_favourite_picture(favourite_picture: FavouritePicture) -> 'Picture':
    return {
        'foreign_id': favourite_picture.foreign_id,
        'url': favourite_picture.url,
    }


def _load_pictures(user_client: Client, pictures: Iterable['Picture']) -> None:
    for picture in pictures:
        user_client.post(
            reverse('pictures:dashboard'),
            data=picture,
        )


@pytest.mark.django_db()
@pytest.mark.parametrize('picture_count', [1, 2, 4, 10, 50, 100])
def test_add_pictures_to_favourites(
    user: User,
    user_client: Client,
    picture_factory: 'PictureFactory',
    picture_count: int,
    _list_eq: _ListEq,
) -> None:
    """This test ensures correctness of saving pictures to favourites."""
    added_pictures: list['Picture'] = [picture_factory() for _ in range(picture_count)]

    _load_pictures(user_client, added_pictures)

    user_pictures = list(map(_convert_favourite_picture, favourite_pictures.by_user(user.id).all()))

    assert _list_eq(added_pictures, user_pictures)


@pytest.mark.django_db()
@pytest.mark.parametrize('times', [1, 2, 4, 10])
def test_add_repetitions_to_favourites(
    user: User,
    user_client: Client,
    picture_factory: 'PictureFactory',
    times: int,
    _list_eq: _ListEq,
) -> None:
    """This test ensures correctness of saving one photo to favourites many times."""
    picture: 'Picture' = picture_factory()
    pictures = [picture for _ in range(times)]

    _load_pictures(user_client, pictures)

    user_pictures = list(map(_convert_favourite_picture, favourite_pictures.by_user(user.id).all()))

    assert _list_eq([picture for _ in range(times)], user_pictures)
