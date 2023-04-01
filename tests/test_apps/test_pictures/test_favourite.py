from collections.abc import Iterable
from http import HTTPStatus
from typing import TYPE_CHECKING, Callable

import pytest
from django.test.client import Client
from django.urls import reverse
from typing_extensions import TypeAlias

from server.apps.identity.models import User
from server.apps.pictures.logic.repo.queries import favourite_pictures
from server.apps.pictures.models import FavouritePicture

if TYPE_CHECKING:
    from tests.plugins.pictures.picture import Picture, PictureFactory
    from tests.plugins.pictures.helper import _ListEq


def _convert_favourite_picture(favourite_picture: FavouritePicture) -> 'Picture':
    return {
        'foreign_id': favourite_picture.foreign_id,
        'url': favourite_picture.url,
    }


FavouriteUploader: TypeAlias = Callable[[Iterable['Picture']], None]


@pytest.fixture()
def _favourite_uploader(user_client: Client) -> FavouriteUploader:
    def _uploader(pictures: Iterable['Picture']) -> None:
        for picture in pictures:
            response = user_client.post(
                reverse('pictures:dashboard'),
                data=picture,
            )

            assert response.status_code == HTTPStatus.FOUND
            assert response.get('Location') == reverse('pictures:dashboard')

    return _uploader


@pytest.mark.django_db()
@pytest.mark.parametrize('picture_count', [1, 2, 4, 10, 50, 100])
def test_add_pictures_to_favourites(
    user: User,
    user_client: Client,
    picture_factory: 'PictureFactory',
    _favourite_uploader: FavouriteUploader,
    picture_count: int,
    assert_list_eq: '_ListEq[Picture]',
) -> None:
    """This test ensures correctness of saving pictures to favourites."""
    added_pictures: list['Picture'] = [picture_factory() for _ in range(picture_count)]

    _favourite_uploader(added_pictures)

    user_pictures = list(map(_convert_favourite_picture, favourite_pictures.by_user(user.id).all()))

    assert_list_eq(added_pictures, user_pictures)


@pytest.mark.django_db()
@pytest.mark.parametrize('times', [1, 2, 4, 10])
def test_add_repetitions_to_favourites(
    user: User,
    user_client: Client,
    picture_factory: 'PictureFactory',
    _favourite_uploader: FavouriteUploader,
    times: int,
    assert_list_eq: '_ListEq[Picture]',
) -> None:
    """This test ensures correctness of saving one photo to favourites many times."""
    picture: 'Picture' = picture_factory()
    pictures = [picture for _ in range(times)]

    _favourite_uploader(pictures)

    user_pictures = list(map(_convert_favourite_picture, favourite_pictures.by_user(user.id).all()))

    assert_list_eq([picture for _ in range(times)], user_pictures)
