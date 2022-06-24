import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-descrp',
        )
        posts = [
            Post(
                author=cls.user,
                text='test-text',
                group=cls.group,
            )
            for post in range(1, 14)
        ]
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_index_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_index_page_contains_three_records(self):
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_group_list_page_contains_ten_records(self):
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug'}
        ))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_group_list_page_contains_three_records(self):
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug'}
        )
            + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_profile_page_contains_ten_records(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'auth'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_page_contains_three_records(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'auth'}
        )
            + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-descrp',
        )
        cls.group_1 = Group.objects.create(
            title='test-group_1',
            slug='test-slug_1',
            description='test-descrp_1',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-text',
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'test-text')
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, 'test-group')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug'}
        ))
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_group_0, 'test-group')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'auth'}
        ))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        ))
        first_object = response.context['post']
        post_id_0 = first_object.id
        post_image_0 = first_object.image
        self.assertEqual(post_id_0, self.post.id)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_create'
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_appear_at_correct_group_page(self):
        """Пост не попал в другую группу."""
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug_1'}
        ))
        first_object = response.context['page_obj']
        self.assertEqual(len(first_object), 0)

    def test_post_appear_at_correct_pages(self):
        """Пост появляется на нужных страницах."""
        pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertIn(self.post, response.context['page_obj'])

    def test_authorized_can_comment(self):
        form_data = {
            'text': 'test_comment'
        }
        self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}
        ),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            self.post.comments.filter(
                text='test_comment'
            ).exists()
        )

    def test_guest_cannot_comment(self):
        form_data = {
            'text': 'test_comment'
        }
        self.guest_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}
        ),
            data=form_data,
            follow=True
        )
        self.assertFalse(
            self.post.comments.filter(
                text='test_comment'
            ).exists()
        )

    def test_comments_appear_correctly(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'test_comment'
        }
        response = self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}
        ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            self.post.comments.filter(
                text='test_comment'
            ).exists()
        )


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='auth_1')
        cls.user_2 = User.objects.create_user(username='auth_2')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-descrp',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_1)

    def test_user_follow_unfollow_correctly(self):
        self.authorized_client.post(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_2.username}
        ))
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_1,
                author=self.user_2,
            ).exists()
        )

    def test_user_unfollow_correctly(self):
        Follow.objects.create(
            user=self.user_1,
            author=self.user_2
        )
        self.authorized_client.post(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_2.username}
        ))
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_1,
                author=self.user_2,
            ).exists()
        )

    def test_followed_posts_apears_corretly(self):
        self.authorized_client.post(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_2.username}
        ))
        post = Post.objects.create(
            author=self.user_2,
            text='test-text',
            group=self.group,
        )
        response_followed = self.authorized_client.get(reverse(
            'posts:follow_index'
        ))
        self.assertIn(post, response_followed.context['page_obj'])
        self.authorized_client.post(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_2.username}
        ))
        response_unfollowed = self.authorized_client.get(reverse(
            'posts:follow_index'
        ))
        self.assertNotIn(post, response_unfollowed.context['page_obj'])
