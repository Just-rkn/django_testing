from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class TestAnonymousUser(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='тестовый читатель')
        cls.author = User.objects.create(username='Тестовый автор')
        cls.note = Note.objects.create(
            title='Текст заголовка', text='Текст заметки', author=cls.author
        )

    def test_pages_available_for_anonymous_user(self):
        urls = (
            'notes:home', 'users:login', 'users:logout', 'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirect_anonymous_user(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:detail', (self.note.id,)),
            ('notes:edit', (self.note.id,)),
            ('notes:delete', (self.note.id,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_available_for_user(self):
        urls = (
            'notes:list', 'notes:success', 'notes:add',
        )
        self.client.force_login(self.reader)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_available_for_author(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:detail', 'notes:edit', 'notes:delete',
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
