from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='тестовый читатель')
        cls.author = User.objects.create(username='Тестовый автор')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.notes_list_url = reverse('notes:list')
        cls.note_add_route = 'notes:add'
        cls.note_edit_route = 'notes:edit'
        cls.note = Note.objects.create(
            title='Текст заголовка', text='Текст заметки', author=cls.author
        )

    def test_notes_list_for_different_users(self):
        users = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for user_client, note_in_list in users:
            with self.subTest(name='note_in_list'):
                response = user_client.get(self.notes_list_url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, note_in_list)

    def test_user_has_form(self):
        users_url = (
            (self.reader, self.note_add_route, None),
            (self.author, self.note_edit_route, (self.note.slug,)),
        )
        for user, name, args in users_url:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.client.force_login(user)
                response = self.client.get(url)
                self.assertIn('form', response.context)
