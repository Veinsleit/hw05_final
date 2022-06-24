from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-descrp',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-text_1',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_cache(self):
        self.authorized_client.get(reverse('posts:index'))
        Post.objects.filter(id=self.post.id).delete()
        response_cache = self.authorized_client.get(reverse('posts:index'))
        self.assertIn(self.post.text.encode(), response_cache.content)
        cache.clear()
        response_cache_cleared = self.authorized_client.get(reverse(
            'posts:index'
        ))
        self.assertNotIn(
            self.post.text.encode(),
            response_cache_cleared.content
        )
