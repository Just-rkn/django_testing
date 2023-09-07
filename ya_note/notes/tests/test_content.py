from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='тестовый читатель')
        cls.author = User.objects.create(username='Тестовый автор')
        cls.note = Note.objects.create(
            title='Текст заголовка', text='Текст заметки', author=cls.author
        )

    def test_notes_list_for_different_users(self):
        users = (
            (self.author, True),
            (self.reader, False),
        )
        for user, note_in_list in users:
            with self.subTest(name='note_in_list'):
                url = reverse('notes:list')
                self.client.force_login(user)
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, note_in_list)

    def test_user_has_form(self):
        users_url = (
            (self.reader, 'notes:add', None),
            (self.author, 'notes:edit', (self.note.slug,)),
        )
        for user, name, args in users_url:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.client.force_login(user)
                response = self.client.get(url)
                self.assertIn('form', response.context)
