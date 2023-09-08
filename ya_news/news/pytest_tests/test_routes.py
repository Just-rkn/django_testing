from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects
import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, kwargs, status, parametrized_client',
    (
        ('news:home', None, HTTPStatus.OK, pytest.lazy_fixture('client')),
        ('users:login', None, HTTPStatus.OK, pytest.lazy_fixture('client')),
        ('users:logout', None, HTTPStatus.OK, pytest.lazy_fixture('client')),
        ('users:signup', None, HTTPStatus.OK, pytest.lazy_fixture('client')),
        (
            'news:detail', pytest.lazy_fixture('news_kwargs_pk'),
            HTTPStatus.OK, pytest.lazy_fixture('client')
        ),
        (
            'news:edit', pytest.lazy_fixture('comment_kwargs_pk'),
            HTTPStatus.NOT_FOUND, pytest.lazy_fixture('admin_client')
        ),
        (
            'news:delete', pytest.lazy_fixture('comment_kwargs_pk'),
            HTTPStatus.NOT_FOUND, pytest.lazy_fixture('admin_client')
        ),
    ),
)
def test_pages_available_for_anonymous_user(
    parametrized_client, name, kwargs, status
):
    url = reverse(name, kwargs=kwargs)
    response = parametrized_client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, status, name, comment
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirect_for_anonymous_client(client, name, comment):
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
