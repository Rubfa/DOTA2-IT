from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Message


class HomeMessageboardPanelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="poster1", password="pass12345")
        self.other_user = user_model.objects.create_user(username="poster2", password="pass12345")
        self.url = f"{reverse('home_test')}?panel=messageboard"

    def test_post_message_creates_home_topic_message(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"text": "Hello market", "parent_id": ""})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.count(), 1)

        message = Message.objects.get()
        self.assertEqual(message.topic_key, "home")
        self.assertEqual(message.author, self.user)

    def test_author_can_delete_own_message_from_home_panel(self):
        self.client.force_login(self.user)
        message = Message.objects.create(author=self.user, topic_key="home", text="Delete me")

        response = self.client.post(self.url, {"delete_message_id": message.id})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Message.objects.filter(id=message.id).exists())

    def test_non_owner_delete_request_does_not_remove_message(self):
        self.client.force_login(self.other_user)
        message = Message.objects.create(author=self.user, topic_key="home", text="Keep me")

        response = self.client.post(self.url, {"delete_message_id": message.id})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Message.objects.filter(id=message.id).exists())
