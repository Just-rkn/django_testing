from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from .ya_note_urls import (
    NOTES_ADD_ROUTE, NOTES_EDIT_ROUTE, NOTES_HOME_ROUTE, NOTES_LIST_ROUTE,
    NOTES_LOGIN_ROUTE, NOTES_DELETE_ROUTE, NOTES_DETAIL_ROUTE,
    NOTES_LOGOUT_ROUTE, NOTES_SIGNUP_ROUTE, NOTES_SUCCESS_ROUTE,
    NOTES_LOGIN_URL,
)

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
            NOTES_HOME_ROUTE, NOTES_LOGIN_ROUTE,
            NOTES_LOGOUT_ROUTE, NOTES_SIGNUP_ROUTE,
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirect_anonymous_user(self):
        urls = (
            (NOTES_DETAIL_ROUTE, (self.note.id,)),
            (NOTES_EDIT_ROUTE, (self.note.id,)),
            (NOTES_DELETE_ROUTE, (self.note.id,)),
            (NOTES_ADD_ROUTE, None),
            (NOTES_SUCCESS_ROUTE, None),
            (NOTES_LIST_ROUTE, None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{NOTES_LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_available_for_user(self):
        urls = (
            NOTES_LIST_ROUTE, NOTES_SUCCESS_ROUTE, NOTES_ADD_ROUTE,
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
            NOTES_DETAIL_ROUTE, NOTES_EDIT_ROUTE, NOTES_DELETE_ROUTE,
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
