from datetime import datetime, timedelta

import pytest
from django.utils import timezone
from django.urls import reverse
from django.db import transaction

from news.models import Comment, News
from news.forms import BAD_WORDS
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def news_kwargs_pk(news):
    return {'pk': news.id}


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def comment_kwargs_pk(comment):
    return {'pk': comment.id}


@pytest.fixture
def news_list_with_different_date():
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text=f'Текст {index}',
            date=today - timedelta(days=index)
        )
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments_list_with_different_date(author, news):
    today = timezone.now()
    with transaction.atomic():
        for index in range(5):
            comment = Comment.objects.create(
                news=news, author=author, text=f'Текст {index}'
            )
            comment.created = today - timedelta(days=index)
            comment.save()


@pytest.fixture
def comment_form_data():
    return {'text': 'Текст комментария'}


@pytest.fixture
def bad_words_data():
    return {'text': f'Текст {BAD_WORDS[0]}'}


@pytest.fixture
def count_comment_before():
    return Comment.objects.count()


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def news_home_url(news):
    return reverse('news:home')
