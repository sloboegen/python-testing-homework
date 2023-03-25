import datetime
from typing import Callable, Protocol, TypedDict, final

import pytest
from django.test.client import Client
from mimesis.locales import Locale
from mimesis.schema import Field, Schema
from typing_extensions import TypeAlias, Unpack

from server.apps.identity.models import User


class UserData(TypedDict, total=False):
    email: str
    first_name: str
    last_name: str
    date_of_birth: datetime.datetime
    address: str
    job_title: str
    phone: str


@final
class RegistrationData(UserData, total=False):
    password1: str
    password2: str


@final
class RegistrationDataFactory(Protocol):
    def __call__(self, **fields: Unpack[RegistrationData]) -> RegistrationData:
        """User data factory protocol."""


@pytest.fixture()
def registration_data_factory(faker_seed: int) -> RegistrationDataFactory:
    def factory(**fields: Unpack[RegistrationData]) -> RegistrationData:
        mf = Field(locale=Locale.RU, seed=faker_seed)
        password = mf('password')
        schema = Schema(schema=lambda: {
            'email': mf('person.email'),
            'first_name': mf('person.first_name'),
            'last_name': mf('person.last_name'),
            'date_of_birth': mf('datetime.date'),
            'address': mf('address.city'),
            'job_title': mf('person.occupation'),
            'phone': mf('person.telephone'),
        })

        return {
            **schema.create(iterations=1)[0],
            **{'password1': password, 'password2': password},
            **fields,
        }

    return factory


@pytest.fixture()
def registration_data(registration_data_factory: RegistrationDataFactory) -> RegistrationData:
    return registration_data_factory()


@pytest.fixture()
def expected_user_data(registration_data: RegistrationData) -> UserData:
    return {
        key_name: value_part
        for key_name, value_part in registration_data.items()
        if not key_name.startswith('password')
    }


@pytest.fixture()
def user(
    registration_data: RegistrationData,
    expected_user_data: UserData
) -> User:
    user = User(**expected_user_data)
    user.set_password(registration_data['password1'])
    user.save()
    print(f'here: {user.password}')
    return user


@pytest.fixture()
def user_client(user: User) -> Client:
    client = Client()
    client.force_login(user)
    return client


UserAssertion: TypeAlias = Callable[[str, RegistrationData], None]


@pytest.fixture(scope='session')
def assert_correct_user() -> UserAssertion:
    def factory(email: str, expected: UserData) -> None:
        user = User.objects.get(email=email)
        # Special fields:
        assert user.id
        assert user.is_active
        assert not user.is_superuser
        assert not user.is_staff
        # All other fields:
        for field_name, data_value in expected.items():
            assert getattr(user, field_name) == data_value

    return factory
