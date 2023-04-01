import json
import os.path
import random
from collections.abc import Iterator
from http import HTTPStatus
from typing import TYPE_CHECKING, TypedDict
from urllib.parse import urljoin

import httpretty
import pytest
from django.test.client import Client
from django.urls import reverse

from server.settings.components import placeholder

if TYPE_CHECKING:
    from tests.plugins.pictures.helper import _ListEq
    from tests.plugins.pictures.picture import Picture, PictureFactory


class PictureData(TypedDict):
    id: int
    url: str


def _convert_picture(picture: 'Picture') -> PictureData:
    return {'id': picture['foreign_id'], 'url': picture['url']}


@pytest.fixture()
def fetching_photos_api_mock(picture_factory: 'PictureFactory') -> Iterator[list['PictureData']]:
    pictures_count = random.randint(a=0, b=10)
    body = [_convert_picture(picture_factory()) for _ in range(pictures_count)]

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


@pytest.fixture(scope='session')
def picture_test_data() -> list[PictureData]:
    with open(os.path.join('tests', 'data', 'db.json')) as f:
        return json.load(f).get('photos')


@pytest.mark.django_db()
def test_dashboard_picture_fetching_mock(
    user_client: Client,
    fetching_photos_api_mock: 'PictureData',
    assert_list_eq: '_ListEq[PictureData]',
) -> None:
    """Test ensures that all pictures from PLACEHOLDER_API_URL/photos (use mock) presents in /dashboard-page."""
    response = user_client.get(reverse('pictures:dashboard'))

    assert response.status_code == HTTPStatus.OK
    assert_list_eq(fetching_photos_api_mock, response.context['pictures'])  # type: ignore[arg-type]


@pytest.mark.django_db()
@pytest.mark.timeout(5)
def test_dashboard_picture_fetching_json_server(
    user_client: Client,
    assert_list_eq: '_ListEq[PictureData]',
    picture_test_data: list[PictureData],
) -> None:
    """Test ensures that all pictures from PLACEHOLDER_API_URL/photos (use json-server) presents in /dashboard-page."""
    response = user_client.get(reverse('pictures:dashboard'))

    assert response.status_code == HTTPStatus.OK
    assert_list_eq(picture_test_data, response.context['pictures'])
