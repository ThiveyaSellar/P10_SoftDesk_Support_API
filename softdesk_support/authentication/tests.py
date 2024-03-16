# Quels tests écrire pour cette ressource ?
# On va y réfléchir et si on trouve pas on va s'aider de ChatGPT
# Si non on va demander au mentor

from django.urls import reverse_lazy
from rest_framework.test import APITestCase, force_authenticate
from rest_framework.authtoken.models import Token

from authentication.models import User

class TestUser(APITestCase):

    url = reverse_lazy('users-list')

    def format_datetime(self,value):
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Test Create a user
    def test_create(self):
        self.assertFalse(User.objects.exists())
        response = self.client.post(
            self.url,
            data={
                "age": 32,
                "username": "user2",
                "password": "user2",
                "can_be_contacted": True,
                "can_data_be_shared": True
            }
        )
        self.assertEqual(response.status_code,201)
        self.assertTrue(User.objects.exists())
        expected = {
            "age": 32,
            "username": "user2",
            "can_be_contacted": True,
            "can_data_be_shared": True,
            "created_time": response.json()["created_time"]
        }
        self.assertEqual(expected, response.json())

    # Test Get a user
    def test_get(self):
        user = User.objects.create(
            username="toto",
            password="toto",
            age=25,
            can_be_contacted=True,
            can_data_be_shared=True
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        expected = [
            {
                "age": 25,
                "username": "toto",
                "can_be_contacted": True,
                "can_data_be_shared": True,
                "created_time": self.format_datetime(user.created_time)
            }
        ]
        self.assertEqual(expected, response.json()["results"])

    """def setAuthorization(self):
        self.user = User.objects.create(username='toto',password='toto')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)"""

    # Test Update a user
    def test_update(self):
        user = User.objects.create(
            username="toto",
            password="toto",
            age=25,
            can_be_contacted=True,
            can_data_be_shared=True
        )
        response = self.client.patch(self.url,data={"age":27})
        force_authenticate(response, user=user)
        self.assertEqual(response.status_code, 200)
        expected = {
            "age": 27,
            "username": "toto",
            "can_be_contacted": True,
            "can_data_be_shared": True,
            "created_time": self.format_datetime(user.created_time)
        }
        self.assertEqual(response.json(), expected)

    # Test Delete a user

    """def test_delete(self):
        self.assertFalse(User.objects.exist())
        response = self.client.post(
            self.url,
            data = {
                "age": 32,
                "username": "user2",
                "password": "user2",
                "can_be_contacted": True,
                "can_data_be_shared": True
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.exist())
        response = self.client.delete(self.url + '',)"""
    # Test Get a list of user