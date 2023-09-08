from http import HTTPStatus

from pytest_django.asserts import assertFormError
import pytest

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    news, comment_form_data, client, count_comment_before,
    news_detail_url
):
    client.post(news_detail_url, data=comment_form_data)
    comments_count = Comment.objects.count()
    assert comments_count == count_comment_before


@pytest.mark.django_db
def test_user_can_create_comment(
    author, author_client, news, comment_form_data, count_comment_before,
    news_detail_url
):
    author_client.post(news_detail_url, data=comment_form_data)
    comments_count = Comment.objects.count()
    assert comments_count == count_comment_before + 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(
    author_client, news, bad_words_data, count_comment_before,
    news_detail_url
):
    response = author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(
        response=response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == count_comment_before


@pytest.mark.django_db
def test_author_can_delete_comment(
    author_client, comment, count_comment_before, comment_delete_url
):
    author_client.post(comment_delete_url)
    comments_count = Comment.objects.count()
    assert comments_count == count_comment_before - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    admin_client, comment, count_comment_before, comment_delete_url
):
    response = admin_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == count_comment_before


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment, comment_edit_url
):
    form_data = {'text': 'Новый текст'}
    author_client.post(comment_edit_url, data=form_data)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    admin_client, comment, comment_edit_url
):
    comment_text = comment.text
    response = admin_client.post(comment_edit_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text
