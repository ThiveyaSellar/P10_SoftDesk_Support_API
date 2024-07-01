from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.urls import reverse_lazy
from rest_framework.test import APITestCase

from .models import User


class SupportAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.admin = User.objects.create_user(
            username="test_admin",
            password="test_admin",
            age=30,
            email="test_admin@support.fr",
            first_name="test_admin",
            last_name="test_admin",
            can_be_contacted=True,
            can_data_be_shared=True,
            is_superuser=True
        )
        cls.user = User.objects.create_user(
            username="user1",
            password="user1",
            age=25,
            email="user1@support.fr",
            first_name="user1",
            last_name="user1",
            can_be_contacted=True,
            can_data_be_shared=True
        )
        cls.author = User.objects.create_user(
            username="user2",
            password="user2",
            age=25,
            email="user2@support.fr",
            first_name="user2",
            last_name="user2",
            can_be_contacted=True,
            can_data_be_shared=True
        )
        cls.collaborator = User.objects.create_user(
            username="user3",
            password="user3",
            age=25,
            email="user3@support.fr",
            first_name="user3",
            last_name="user3",
            can_be_contacted=True,
            can_data_be_shared=True
        )

    def format_datetime(self, value):
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class TestUser(SupportAPITestCase):

    # Tester les endpoints
    # En faisant des requêtes vers les endpoints
    # Observer si ce qu'on obtient est bien ce qu'on attend
    url_list = reverse_lazy('users-list')
    url_detail = reverse_lazy('users-detail', args=[2])

    # Create a user by signing up
    def test_signing_up(self):
        response = self.client.post(
            '/api/sign-up/',
            data={
                "username": "toto",
                "password": "toto",
                "password2": "toto",
                "age": 25,
                "email": "toto@toto.fr",
                "first_name": "toto",
                "last_name": "toto",
                "can_be_contacted": True,
                "can_data_be_shared": True
            }
        )
        self.assertTrue(response.status_code, 201)
        expected = {
            "username": "toto",
            "password": "toto",
            "password2": "toto",
            "age": 25,
            "email": "toto@toto.fr",
            "first_name": "toto",
            "last_name": "toto",
            "can_be_contacted": True,
            "can_data_be_shared": True,
        }

        self.assertEqual(response.json(), expected)

    def test_username_already_exists(self):

        response = self.client.post(
            '/api/sign-up/',
            data={
                "username": "user1",
                "password": "user2",
                "password2": "user2",
                "age": 25,
                "email": "user2@user2.fr",
                "first_name": "user2",
                "last_name": "user2",
                "can_be_contacted": True,
                "can_data_be_shared": True
            }
        )
        self.assertTrue(response.status_code, 400)

    def test_email_already_exists(self):

        response = self.client.post(
            '/api/sign-up/',
            data={
                "username": "user2",
                "password": "user2",
                "password2": "user2",
                "age": 25,
                "email": "user1@user1.fr",
                "first_name": "user2",
                "last_name": "user2",
                "can_be_contacted": True,
                "can_data_be_shared": True
            }
        )
        self.assertTrue(response.status_code, 400)

    def test_logging(self):
        response = self.client.post(
            '/api/login/',
            data={
                "username": "user1",
                "password": "user1"
            }
        )
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())

    def support_api_authentication(self, username, password):
        response = self.client.post(
            '/api/login/',
            data={
                "username": username,
                "password": password
            }
        )
        access = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def test_create_as_admin(self):

        self.support_api_authentication("test_admin", "test_admin")

        def check_user_existence(username, email):
            try:
                User.objects.get(Q(username=username) | Q(email=email))
                return True
            except ObjectDoesNotExist:
                return False

        self.assertFalse(check_user_existence("user4", "user4@support.fr"))

        response = self.client.post(
            self.url_list,
            data={
                "username": "user4",
                "password": "user4",
                "password2": "user4",
                "age": 25,
                "email": "user4@support.fr",
                "first_name": "user4",
                "last_name": "user4",
                "can_be_contacted": True,
                "can_data_be_shared": True
            }
        )
        self.assertEqual(response.status_code, 201)
        expected = {
            "username": "user4",
            "age": 25,
            "email": "user4@support.fr",
            "first_name": "user4",
            "last_name": "user4",
            "can_be_contacted": True,
            "can_data_be_shared": True,
            "created_time": response.json()["created_time"]
        }
        self.assertEqual(expected, response.json())
        self.assertTrue(check_user_existence("user4", "user4@support.fr"))

    def test_create_as_user(self):

        self.support_api_authentication("user1", "user1")

        def check_user_existence(username, email):
            try:
                User.objects.get(Q(username=username) | Q(email=email))
                return True
            except ObjectDoesNotExist:
                return False

        self.assertFalse(check_user_existence("user4", "user4@support.fr"))

        response = self.client.post(
            self.url_list,
            data={
                "username": "user4",
                "password": "user4",
                "password2": "user4",
                "age": 25,
                "email": "user4@support.fr",
                "first_name": "user4",
                "last_name": "user4",
                "can_be_contacted": True,
                "can_data_be_shared": True
            }
        )
        self.assertEqual(response.status_code, 201)
        expected = {
            "username": "user4",
            "age": 25,
            "email": "user4@support.fr",
            "first_name": "user4",
            "last_name": "user4",
            "can_be_contacted": True,
            "can_data_be_shared": True,
            "created_time": response.json()["created_time"]
        }
        self.assertEqual(expected, response.json())
        self.assertTrue(check_user_existence("user4", "user4@support.fr"))

    def test_get_users(self):
        users = User.objects.all()
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        expected = [
            {
                "username": "test_admin",
                "age": 30,
                "email": "test_admin@support.fr",
                "first_name": "test_admin",
                "last_name": "test_admin",
                "can_be_contacted": True,
                "can_data_be_shared": True,
                "created_time": self.format_datetime(users[0].created_time)
            },
            {
                "username": "user1",
                "age": 25,
                "email": "user1@support.fr",
                "first_name": "user1",
                "last_name": "user1",
                "can_be_contacted": True,
                "can_data_be_shared": True,
                "created_time": self.format_datetime(users[1].created_time)
            },
            {
                "username": "user2",
                "age": 25,
                "email": "user2@support.fr",
                "first_name": "user2",
                "last_name": "user2",
                "can_be_contacted": True,
                "can_data_be_shared": True,
                "created_time": self.format_datetime(users[2].created_time)
            },
            {
                "username": "user3",
                "age": 25,
                "email": "user3@support.fr",
                "first_name": "user3",
                "last_name": "user3",
                "can_be_contacted": True,
                "can_data_be_shared": True,
                "created_time": self.format_datetime(users[3].created_time)
            }
        ]
        self.assertEqual(expected, response.json()["results"])

    def test_get_user(self):
        user = User.objects.get(pk=2)
        response = self.client.get("/api/users/2/")
        self.assertEqual(response.status_code, 200)
        expected = {
            "username": "user1",
            "age": 25,
            "email": "user1@support.fr",
            "first_name": "user1",
            "last_name": "user1",
            "can_be_contacted": True,
            "can_data_be_shared": True,
            "created_time": self.format_datetime(user.created_time)
        }
        self.assertEqual(expected, response.json())

    def test_update(self):
        user = User.objects.get(pk=2)

        self.support_api_authentication("user1", "user1")

        response = self.client.patch(self.url_detail, data={"age": 27})
        self.assertEqual(response.status_code, 200)
        expected = {
            "username": "user1",
            "age": 27,
            "email": "user1@support.fr",
            "first_name": "user1",
            "last_name": "user1",
            "can_be_contacted": True,
            "can_data_be_shared": True,
            "created_time": self.format_datetime(user.created_time)
        }
        self.assertEqual(response.json(), expected)

    def test_delete(self):
        self.assertTrue(User.objects.filter(username="user1").exists())

        # Authentication
        self.support_api_authentication("user1", "user1")

        # Deletion
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 204)

        self.assertFalse(User.objects.filter(username="user1").exists())
