import logging
import sys

from django.db.models import Q
from django.test import TestCase, Client
from django.urls import reverse

from questions.models import QuestionCategory
from users.models import MyUser
from ..models import Post

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)


class TestPostBase(TestCase):
    """Basic test class for a single setUp and keeping the DRY principle"""

    def setUp(self):
        self.client = Client()
        self.test_user_01 = MyUser.objects.create_user(username='test_01',
                                                       first_name='Roland',
                                                       last_name='Emmerich',
                                                       email='blabla@bla.ru',
                                                       is_active=True)
        self.test_user_02 = MyUser.objects.create_user(username='test_02',
                                                       first_name='Quentin',
                                                       last_name='Tarantino',
                                                       score=5,
                                                       email='blabla@blabla.ru',
                                                       is_active=True)
        self.test_user_01.set_password('laLA12')
        self.test_user_02.set_password('laLA12')
        self.test_user_01.save()
        self.test_user_02.save()

        self.test_category_01 = QuestionCategory.objects.create(name='Disasters')
        self.test_category_02 = QuestionCategory.objects.create(name='Strange_movies')
        self.test_category_03 = QuestionCategory.objects.create(name='Bad_movies', available=False)

        self.test_post_01 = Post.objects.create(title='The Day After Tomorrow',
                                                author=self.test_user_01,
                                                category=self.test_category_01,
                                                body='text about this movie',
                                                tag='post-apocalypse',
                                                available=True)
        self.test_post_02 = Post.objects.create(title='Moon fall',
                                                author=self.test_user_01,
                                                category=self.test_category_01,
                                                body='text about this movie',
                                                tag='fantastic',
                                                available=True)
        self.test_post_03 = Post.objects.create(title='Django Unchained',
                                                author=self.test_user_02,
                                                category=self.test_category_02,
                                                body='text about this movie',
                                                tag='drama',
                                                available=True)
        self.test_post_04 = Post.objects.create(title='The Hateful Eight',
                                                author=self.test_user_02,
                                                category=self.test_category_02,
                                                body='text about this movie',
                                                tag='drama',
                                                available=True)
        self.test_post_05 = Post.objects.create(title='Kill Bill',
                                                author=self.test_user_02,
                                                category=self.test_category_03,
                                                body='text about this movie',
                                                tag='action movie',
                                                available=False)


class TestPostsCategoryView(TestPostBase):
    """Testing PostsCategoryView"""

    def setUp(self):
        super().setUp()

    def test_queryset_only_available_categories(self):
        """Tests PostsCategoryView view that only categories with the available field with the value True
        gets into the queryset"""
        response = self.client.get(reverse('posts:all'))
        categories = QuestionCategory.objects.filter(available=True)
        for categories_set in zip(response.context['posts_categories'], categories):
            self.assertEqual(*categories_set)
        self.assertEqual(response.context['title'], 'Посты')
        self.assertTemplateUsed(response, 'posts/all.html')

    def test_no_inactive_categories_in_queryset(self):
        """Checks that inactive categories do not fall into the queryset"""
        response = self.client.get(reverse('posts:all'))
        category = self.test_category_03
        self.assertNotIn(category, response.context['posts_categories'])


class TestPostView(TestPostBase):
    """Testing PostView"""

    def setUp(self):
        super().setUp()

    def test_displaying_desired_post(self):
        """Tests PostsView view to get the correct requested post"""
        response = self.client.get(path='/posts/post/2/')
        current_post = Post.objects.get(id=2)
        self.assertEqual(current_post, response.context['post'])
        self.assertEqual(response.context['title'], current_post.title)
        self.assertTemplateUsed(response, 'posts/read.html')


class TestUserPostView(TestPostBase):
    """Testing UserPostView"""

    def setUp(self):
        super().setUp()

    def test_displays_authors_posts_only_for_authorized_users(self):
        """Checks that UserPostView view and relevant site page are only available to authorized users"""
        current_user_id = self.test_user_02.id
        response = self.client.get(path=f'/posts/user_posts/{current_user_id}/')
        self.assertEqual(response.url, f'/users/login/?next=/posts/user_posts/{current_user_id}/')
        self.assertEqual(response.status_code, 302)

    def test_displays_authors_posts(self):
        """Checks UserPostView view to get the correct user and a list of posts where he is the author"""
        self.client.login(username=self.test_user_01.username, password='laLA12')
        current_user_id = self.test_user_02.id

        response = self.client.get(path=f'/posts/user_posts/{current_user_id}/')
        current_user = MyUser.objects.get(id=current_user_id)
        self.assertEqual(current_user, response.context['user'])

        user_posts = Post.objects.filter(Q(author=current_user), Q(available=True))
        self.assertQuerysetEqual(response.context['user_posts'], user_posts, ordered=False)
        self.assertEqual(response.context['title'], f'Посты пользователя {current_user}')
        self.assertTemplateUsed(response, 'posts/user_posts.html')

    def test_no_inactive_posts_in_queryset_author(self):
        """Checks that inactive posts do not fall into the queryset even if they belong to this author"""
        self.client.login(username=self.test_user_01.username, password='laLA12')
        current_user_id = self.test_user_02.id
        response = self.client.get(path=f'/posts/user_posts/{current_user_id}/')

        post = self.test_post_05
        self.assertNotIn(post, response.context['user_posts'])


class TestTagPostView(TestPostBase):
    """Testing TagPostView"""

    def setUp(self):
        super().setUp()

    def test_displays_tag_posts(self):
        """Checks TagPostView view to get the correct tag and a list of posts with this tag"""
        current_tag = 'drama'
        response = self.client.get(path='/posts/tag_posts/drama/')
        tag_posts = Post.objects.filter(Q(tag=current_tag), Q(available=True))
        self.assertQuerysetEqual(response.context['tag_posts'], tag_posts, ordered=False)
        self.assertEqual(response.context['title'], f'Посты с тегом {current_tag}')
        self.assertTemplateUsed(response, 'posts/tag_posts.html')

    def test_no_inactive_posts_in_queryset_tag(self):
        """Checks that inactive posts do not fall into the queryset even if they belong to this tag"""
        response = self.client.get(path='/posts/tag_posts/action%20movie/')
        post = self.test_post_05
        self.assertNotIn(post, response.context['tag_posts'])


class TestCategoryPostView(TestPostBase):
    """Testing CategoryPostView"""

    def setUp(self):
        super().setUp()

    def test_displays_category_posts(self):
        """Checks CategoryPostView view to get the correct category and a list of posts of this category"""
        current_category_id = self.test_category_02.id
        response = self.client.get(path=f'/posts/category_posts/{current_category_id}/')
        category_posts = Post.objects.filter(Q(category=current_category_id), Q(available=True))
        self.assertQuerysetEqual(response.context['category_posts'], category_posts, ordered=False)
        self.assertEqual(response.context['title'], f'Посты категории {self.test_category_02}')
        self.assertTemplateUsed(response, 'posts/category_posts.html')

    def test_no_inactive_posts_in_queryset_category(self):
        """Checks that inactive posts do not fall into the queryset
        if they belong to an inactive category or the post itself is inactive"""
        current_category_id = self.test_category_03.id
        response = self.client.get(path=f'/posts/category_posts/{current_category_id}/')
        post = self.test_post_05
        self.assertNotIn(post, response.context['category_posts'])

        current_category_id = self.test_category_02.id
        response = self.client.get(path=f'/posts/category_posts/{current_category_id}/')
        post = self.test_post_03
        self.assertIn(post, response.context['category_posts'])

        post.available = False
        post.save()
        response = self.client.get(path=f'/posts/category_posts/{current_category_id}/')
        self.assertNotIn(post, response.context['category_posts'])
        post.available = True
        post.save()


class TestSearchPostView(TestPostBase):
    """Testing SearchPostView"""

    def setUp(self):
        super().setUp()

    def test_displays_search_posts(self):
        """Checks SearchPostView view to get the correct queryset of posts, according to the search options:
            - by tag;
            - by the title;
            - by the part of tag or of title;"""
        searchable_tag = 'post-apocalypse'
        searchable_title = 'Django'
        searchable_part = 'a'

        for item in (searchable_tag, searchable_title, searchable_part):
            response = self.client.get(f'/posts/search/?search_panel={item}/',
                                       {'search_panel': item})
            object_list = Post.objects.filter(Q(title__icontains=item) |
                                              Q(tag__icontains=item)).filter(available=True)
            self.assertQuerysetEqual(response.context['object_list'], object_list, ordered=False)

        self.assertEqual(response.context['title'], 'Поиск статьи')
        self.assertTemplateUsed(response, 'posts/search_results_post.html')

    def test_no_inactive_posts_in_queryset_search(self):
        """Checks that inactive posts do not fall into the search queryset"""
        searchable_part = 'i'
        response = self.client.get(f'/posts/search/?search_panel={searchable_part}/',
                                   {'search_panel': searchable_part})

        post = self.test_post_05
        self.assertNotIn(post, response.context['object_list'])
