from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Note, NoteUpdate

class NoteAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpassword123')
        cls.login_url = reverse('token_obtain_pair')
        cls.create_note_url = reverse('create_note') 

    def setUp(self):
        self.login_and_set_token('testuser', 'testpassword123')

    def login_and_set_token(self, username, password):
        resp = self.client.post(self.login_url, {'username': username, 'password': password})
        token = resp.data['access'] 
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def create_note(self, title, content, user=None):
        note = Note.objects.create(title=title, content=content, owner=user or self.user)
        return note

    # Create Notes
    def test_create_note_success(self):
        data = {'title': 'Test Note', 'content': 'This is a test note.'}
        response = self.client.post(self.create_note_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Note.objects.filter(title='Test Note').exists())

    def test_create_note_unauthorized(self):
        self.client.credentials() 
        data = {'title': 'Test Note', 'content': 'This is a test note.'}
        response = self.client.post(self.create_note_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Get Specific Note
    def test_get_note_success(self):
        note = self.create_note('Owned Note', 'This note is owned by the test user.')
        url = reverse('retrieve_note', kwargs={'id': note.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], note.title)

    def test_get_note_unauthorized(self):
        note = self.create_note('Another Note', 'This note is private.')
        url = reverse('retrieve_note', kwargs={'id': note.id})
        self.client.credentials() 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_note_forbidden(self):
        another_user = User.objects.create_user(username='anotheruser', password='password123')
        note = self.create_note('Private Note', 'This note should not be accessible by another user.')
        url = reverse('retrieve_note', kwargs={'id': note.id})
        self.login_and_set_token('anotheruser', 'password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Update Notes
    def test_update_note_success(self):
        note = self.create_note('Initial Title', 'Initial content.')
        update_url = reverse('retrieve_note', kwargs={'id': note.id}) 
        updated_data = {'title': 'Updated Title', 'content': 'Updated content.'}
        response = self.client.put(update_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()

    def test_update_note_unauthorized(self):
        note = self.create_note('Some Title', 'Some content.')
        self.client.credentials()
        update_url = reverse('retrieve_note', kwargs={'id': note.id})
        response = self.client.put(update_url, {'title': 'New Title', 'content': 'New content.'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_note_forbidden(self):
        another_user = User.objects.create_user(username='anotheruser', password='password123')
        note = self.create_note('Some Title', 'Some content.')
        self.login_and_set_token('anotheruser', 'password123')
        update_url = reverse('retrieve_note', kwargs={'id': note.id})
        response = self.client.put(update_url, {'title': 'New Title', 'content': 'New content.'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Share a Note
    def test_share_note_success(self):
        note = self.create_note('Shareable Note', 'This note will be shared.')
        share_url = reverse('share_note') 
        user2 = User.objects.create_user('user2', 'password123')
        user3 = User.objects.create_user('user3', 'password123')
        share_data = {'note_id': note.id, 'user_ids': [user2.id, user3.id]}
        response = self.client.post(share_url, share_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertIn(user2, note.shared_with.all())
        self.assertIn(user3, note.shared_with.all())

    def test_share_note_unauthorized(self):
        share_url = reverse('share_note')
        self.client.credentials() 
        response = self.client.post(share_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class NoteVersionHistoryAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('owner', 'owner@example.com', 'password')
        cls.shared_user = User.objects.create_user('shared_user', 'shared@example.com', 'password')
        cls.unauthorized_user = User.objects.create_user('unauth_user', 'unauth@example.com', 'password')
        cls.note = Note.objects.create(title="Original Title", content="Original Content", owner=cls.owner)
        cls.note.shared_with.add(cls.shared_user)
        NoteUpdate.objects.create(note=cls.note, changed_by=cls.owner, content="First Update Content")
        NoteUpdate.objects.create(note=cls.note, changed_by=cls.shared_user, content="Second Update Content")
        cls.version_history_url = reverse('note_version_history', kwargs={'id': cls.note.id})

    def login_and_set_token(self, user):
        login_url = reverse('token_obtain_pair')
        resp = self.client.post(login_url, {'username': user.username, 'password': 'password'})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])

    def test_version_history_access_by_owner(self):
        self.login_and_set_token(self.owner)
        response = self.client.get(self.version_history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_version_history_access_by_shared_user(self):
        self.login_and_set_token(self.shared_user)
        response = self.client.get(self.version_history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_version_history_access_unauthorized_user(self):
        self.login_and_set_token(self.unauthorized_user)
        response = self.client.get(self.version_history_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_version_history_detail_check(self):
        self.login_and_set_token(self.owner)
        response = self.client.get(self.version_history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        update_data = response.data[0]
        self.assertIn('changed_by', update_data)
        self.assertIn('content', update_data)
        self.assertIn('timestamp', update_data)
