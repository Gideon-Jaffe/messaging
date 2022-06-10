from asyncore import read
from email import message
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from . import serializers
from.models import Message


def create_user():
    testUser = User.objects.create_user(username="testMan", password="ImTesting", email="testing@gmail.com", first_name="Hi", last_name="Im Sure")
    return testUser

# Create your tests here.

class PostmanRegisterViewTests(TestCase):
    def test_register(self):
        data = {"username":"testMan", "password":"ImTesting", "password2":"ImTesting", "email":"testing@gmail.com", "first_name":"Hi", "last_name":"Im Sure"}
        response = self.client.post(reverse('postman:register'), data)
        self.assertEqual(response.status_code, 202)

    def test_register_without_username(self):
        data = {"password":"ImTesting", "password2":"ImTesting", "email":"testing@gmail.com", "first_name":"Hi", "last_name":"Im Sure"}
        response = self.client.post(reverse('postman:register'), data)
        self.assertEqual(response.status_code, 400)


    def test_register_without_password(self):
        data = {"username":"testMan", "password2":"ImTesting", "email":"testing@gmail.com", "first_name":"Hi", "last_name":"Im Sure"}
        response = self.client.post(reverse('postman:register'), data)
        self.assertEqual(response.status_code, 400)


    def test_register_without_password2(self):
        data = {"username":"testMan", "password":"ImTesting", "email":"testing@gmail.com", "first_name":"Hi", "last_name":"Im Sure"}
        response = self.client.post(reverse('postman:register'), data)
        self.assertEqual(response.status_code, 400)

    def test_register_without_email(self):
        data = {"username":"testMan", "password":"ImTesting", "password2":"ImTesting", "first_name":"Hi", "last_name":"Im Sure"}
        response = self.client.post(reverse('postman:register'), data)
        self.assertEqual(response.status_code, 400)

    def test_register_without_first_name(self):
        data = {"username":"testMan", "password":"ImTesting", "password2":"ImTesting", "email":"testing@gmail.com", "last_name":"Im Sure"}
        response = self.client.post(reverse('postman:register'), data)
        self.assertEqual(response.status_code, 400)

    def test_register_without_last_name(self):
        data = {"username":"testMan", "password":"ImTesting", "password2":"ImTesting", "email":"testing@gmail.com", "first_name":"Hi"}
        response = self.client.post(reverse('postman:register'), data)
        self.assertEqual(response.status_code, 400)


class PostmanLoginViewTests(APITestCase):
    def test_login(self):
        self.user = create_user()
        data= {"username":"testMan", "password":"ImTesting"}
        response = self.client.post(reverse('postman:login'), data=data)
        self.assertEqual(response.status_code, 202)

    def test_unregistered_login(self):
        data = {"username":"Bob", "password":"True"}
        response = self.client.post(reverse('postman:login'), data=data)
        self.assertNotEqual(response.status_code, 202)


class PostmanMessagesViewTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testMan", password="ImTesting", email="testing@gmail.com", first_name="Frel", last_name="Jord")
        self.user2 = User.objects.create_user(username="testMan2", password="ImTesting2", email="testing2@gmail.com", first_name="Berg", last_name="Son")

    def test_no_messages(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        response = client.get(reverse('postman:messages'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[]')

    def test_no_messages_to_user(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        Message.objects.create(sender=self.user1, receiver=self.user2, message="Hello", subject="Testing")
        response = client.get(reverse('postman:messages'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[]')

    def test_messages_to_user(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        msg1 = Message.objects.create(sender=self.user2, receiver=self.user1, message="Hello", subject="Testing")
        msg2 = Message.objects.create(sender=self.user2, receiver=self.user1, message="Hello2", subject="Testing2")
        response = client.get(reverse('postman:messages'))
        data = response.json()
        serializer = serializers.MessageSerializer(data = data, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data.__len__(), 2)

    def test_not_logged_in(self):
        client = APIClient()
        response = client.get(reverse('postman:messages'))
        self.assertEqual(response.status_code, 403)

    def test_create_message_not_logged_in(self):
        client = APIClient()
        data = {"receiver":"testMan2", "message":"Hello", "subject":"Meeting"}
        response = client.post(reverse('postman:messages'), data=data)
        self.assertEqual(response.status_code, 403)
        self.assertQuerysetEqual(Message.objects.all(), [])

    def test_create_message(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        data = {"receiver":"testMan2", "message":"Hello", "subject":"Meeting"}
        response = client.post(reverse('postman:messages'), data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Message.objects.all().first().__str__(), Message(sender=self.user1, receiver=self.user2, message="Hello", subject="Meeting").__str__())
    
    def test_create_message_no_receiver(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        data = {"message":"Hello", "subject":"Meeting"}
        response = client.post(reverse('postman:messages'), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertQuerysetEqual(Message.objects.all(), [])

    def test_create_message_no_message(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        data = {"receiver":"testMan2", "subject":"Meeting"}
        response = client.post(reverse('postman:messages'), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertQuerysetEqual(Message.objects.all(), [])

    def test_create_message_no_subject(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        data = {"receiver":"testMan2", "message":"Hello"}
        response = client.post(reverse('postman:messages'), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertQuerysetEqual(Message.objects.all(), [])

class PostmanUnreadMessagesViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testMan", password="ImTesting", email="testing@gmail.com", first_name="Frel", last_name="Jord")
        self.user2 = User.objects.create_user(username="testMan2", password="ImTesting2", email="testing2@gmail.com", first_name="Berg", last_name="Son")
        self.url = reverse('postman:unread_messages')

    def test_no_messages(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[]')

    def test_no_messages_to_user(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        Message.objects.create(sender=self.user1, receiver=self.user2, message="Hello", subject="Testing")
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[]')

    def test_messages_to_user(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        msg1 = Message.objects.create(sender=self.user2, receiver=self.user1, message="Hello", subject="Testing")
        msg2 = Message.objects.create(sender=self.user2, receiver=self.user1, message="Hello2", subject="Testing2")
        response = client.get(self.url)
        data = response.json()
        serializer = serializers.MessageSerializer(data = data, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data.__len__(), 2)

    def test_not_logged_in(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_messages_read(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        msg1 = Message.objects.create(sender=self.user2, receiver=self.user1, message="Hello", subject="Testing")
        msg2 = Message.objects.create(sender=self.user2, receiver=self.user1, message="Hello2", subject="Testing2", read=True)
        response = client.get(self.url)
        data = response.json()
        serializer = serializers.MessageSerializer(data = data, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data.__len__(), 1)

class PostmanUserMessagesView(TestCase):
    def setUp(self):
        self.my_admin = User.objects.create_superuser(username='super', password='superpassword', email='test@gmail.com')
        self.user1 = User.objects.create_user(username="testMan", password="ImTesting", email="testing@gmail.com", first_name="Frel", last_name="Jord")
        self.user2 = User.objects.create_user(username="testMan2", password="ImTesting2", email="testing2@gmail.com", first_name="Berg", last_name="Son")
        self.url = reverse('postman:user_messages', args=(self.user1.pk,))

    def test_not_logged_in(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_not_admin(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        response = client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_no_messages(self):
        client = APIClient()
        client.login(username="super", password="superpassword")
        response = client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_messages_to_user(self):
        client = APIClient()
        client.login(username="super", password="superpassword")
        msg1 = Message.objects.create(sender=self.user2, receiver=self.user1, message="Hello", subject="Testing")
        msg2 = Message.objects.create(sender=self.user2, receiver=self.user1, message="Hello2", subject="Testing2")
        response = client.get(self.url)
        data = response.json()
        serializer = serializers.MessageSerializer(data = data, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data.__len__(), 2)

    def test_no_messages_for_user(self):
        client = APIClient()
        client.login(username="super", password="superpassword")
        msg1 = Message.objects.create(sender=self.user1, receiver=self.user2, message="Hello", subject="Testing")
        msg2 = Message.objects.create(sender=self.user1, receiver=self.user2, message="Hello2", subject="Testing2")
        response = client.get(self.url)
        data = response.json()
        serializer = serializers.MessageSerializer(data = data, many=True)
        self.assertEqual(response.status_code, 404)

    def test_messages_for_two_users(self):
        client = APIClient()
        client.login(username="super", password="superpassword")
        msg1 = Message.objects.create(sender=self.user2, receiver=self.user1, message="Hello", subject="Testing")
        msg2 = Message.objects.create(sender=self.user1, receiver=self.user2, message="Hello2", subject="Testing2")
        response = client.get(self.url)
        data = response.json()
        serializer = serializers.MessageSerializer(data = data, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data.__len__(), 1)

class PostmanSingleMessageViewTest(TestCase):
    def setUp(self):
        self.my_admin = User.objects.create_superuser(username='super', password='superpassword', email='test@gmail.com')
        self.user1 = User.objects.create_user(username="testMan", password="ImTesting", email="testing@gmail.com", first_name="Frel", last_name="Jord")
        self.user2 = User.objects.create_user(username="testMan2", password="ImTesting2", email="testing2@gmail.com", first_name="Berg", last_name="Son")
        self.url_view = 'postman:single_message'

    def test_not_logged_in(self):
        client = APIClient()
        response = client.get(reverse(self.url_view, args=(1, )))
        self.assertEqual(response.status_code, 403)

    def test_no_such_message(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        response = client.get(reverse(self.url_view, args=(1, )))
        self.assertEqual(response.status_code, 404)

    def test_get_others_message(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        msg1 = Message.objects.create(sender=self.user2, receiver=self.user2, message="Hello", subject="Testing")
        response = client.get(reverse(self.url_view, args=(msg1.pk, )))
        self.assertEqual(response.status_code, 403)

    def test_get_message(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        msg1 = Message.objects.create(sender=self.user2, receiver=self.user1, message="Hello", subject="Testing")
        response = client.get(reverse(self.url_view, args=(msg1.pk,)))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        serializer = serializers.MessageSerializer(data = data)  
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data['pk'], msg1)

    def test_delete_no_such_message(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        response = client.delete(reverse(self.url_view, args=(1, )))
        self.assertEqual(response.status_code, 404)

    def test_delete_others_message(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        msg1 = Message.objects.create(sender=self.user2, receiver=self.user2, message="Hello", subject="Testing")
        response = client.delete(reverse(self.url_view, args=(msg1.pk, )))
        self.assertEqual(response.status_code, 403)

    def test_delete_message(self):
        client = APIClient()
        client.login(username="testMan", password="ImTesting")
        msg1 = Message.objects.create(sender=self.user2, receiver=self.user1, message="Hello", subject="Testing")
        response = client.delete(reverse(self.url_view, args=(msg1.pk,)))
        self.assertEqual(response.status_code, 204)
        self.assertQuerysetEqual(Message.objects.all(), [])