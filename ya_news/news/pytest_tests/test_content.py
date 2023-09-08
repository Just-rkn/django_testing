import pytest

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_count_in_home_page(
    news_list_with_different_date, client, news_home_url
):
    response = client.get(news_home_url)
    object_list = response.context['object_list']
    assert object_list.count() == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(news_list_with_different_date, client, news_home_url):
    response = client.get(news_home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(
    comments_list_with_different_date, client, news, news_detail_url
):
    response = client.get(news_detail_url)
    comment_list = response.context['news'].comment_set.all()
    all_dates = [comment.created for comment in comment_list]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, has_form',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False)
    )
)
def test_client_has_form(
    news, parametrized_client, has_form, news_detail_url
):
    response = parametrized_client.get(news_detail_url)
    assert ('form' in response.context) is has_form
