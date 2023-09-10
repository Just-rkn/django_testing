from http import HTTPStatus

from pytils.translit import slugify
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import WARNING
from .ya_note_urls import (
    NOTES_SUCCESS_URL, NOTES_LOGIN_URL, NOTES_ADD_URL,
    NOTES_EDIT_ROUTE, NOTES_DELETE_ROUTE,
)

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Тестовый читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author = User.objects.create(username='Тестовый автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )
        cls.delete_url = reverse(NOTES_DELETE_ROUTE, args=(cls.note.slug,))
        cls.edit_url = reverse(NOTES_EDIT_ROUTE, args=(cls.note.slug,))
        cls.form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'slug': 'test-slug',
        }

    def setUp(self):
        self.count_notes_before = Note.objects.count()

    def test_user_can_create_note(self):
        response = self.author_client.post(NOTES_ADD_URL, data=self.form_data)
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), self.count_notes_before + 1)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(NOTES_ADD_URL, data=self.form_data)
        expected_url = f'{NOTES_LOGIN_URL}?next={NOTES_ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), self.count_notes_before)

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        response = self.reader_client.post(NOTES_ADD_URL, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), self.count_notes_before)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.reader_client.post(NOTES_ADD_URL, data=self.form_data)
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), self.count_notes_before + 1)
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), self.count_notes_before - 1)

    def test_other_user_cant_delete_note(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.count_notes_before)
