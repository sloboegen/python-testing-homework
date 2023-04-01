import contextlib
import json
from http import HTTPStatus

from typing_extensions import TypeAlias
from urllib.parse import urljoin

import pytest
import httpretty

from django.test.client import Client

from django.urls import reverse

from server.settings.components import placeholder

from typing import TYPE_CHECKING, TypedDict, Optional, Callable

from collections.abc import Iterator

if TYPE_CHECKING:
    from tests.plugins.pictures.picture import PictureFactory
    from tests.plugins.pictures.helper import _ListEq


class PictureData(TypedDict):
    id: int
    url: str


FetchingPhotosAPI: TypeAlias = Callable[[Optional[list[PictureData]]], Iterator[PictureData]]


@pytest.fixture()
def fetching_photos_api_mock(picture_factory: 'PictureFactory') -> FetchingPhotosAPI:
    """Context-manager mock for PLACEHOLDER_API_URL/photos that enables body customization."""

    @contextlib.contextmanager
    def inner(body: Optional[list[PictureData]] = None) -> Iterator[PictureData]:
        if body is None:
            picture = picture_factory()
            body = [{'id': picture['foreign_id'], 'url': picture['url']}]

        with httpretty.httprettized():
            httpretty.register_uri(
                method=httpretty.GET,
                uri=urljoin(placeholder.PLACEHOLDER_API_URL, 'photos'),
                body=json.dumps(body),
                status=200,
                content_type='application/json',
            )

            yield body

            httpretty.has_request()

    return inner


@pytest.mark.django_db()
def test_dashboard_picture_fetching(
    user_client: Client,
    fetching_photos_api_mock: FetchingPhotosAPI,
    assert_list_eq: '_ListEq[PictureData]',
) -> None:
    with fetching_photos_api_mock() as body:
        response = user_client.get(reverse('pictures:dashboard'))

        assert response.status_code == HTTPStatus.OK
        assert_list_eq(body, response.context['pictures'])


