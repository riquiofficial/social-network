from django.test import TestCase, Client
from selenium import webdriver
from seleniumlogin import force_login
from selenium.webdriver.common.keys import Keys
import time
from .models import User, Post

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

# Create your tests here.


class Tests(TestCase):

    def setUp(self):
        # Users

        user1 = User.objects.create(
            username="quigl", email="test@example.com")
        user1.set_password("testpass1")
        user1.save()
        user2 = User.objects.create(
            username="bfly87", password="testpass1", email="example@test.com")

        # Posts
        post1 = Post.objects.create(
            author=user1, content="hey how are you all?")
        post2 = Post.objects.create(
            author=user2, content="I'm good, how are you?")
        post3 = Post.objects.create(author=user2, content=("A"*251))

    # SERVER TESTS
    # LIKE POST
    def test_no_likes_count(self):
        user1 = User.objects.get(username="quigl")
        post1 = Post.objects.get(author=user1)

        self.assertEqual(post1.total_likes(), 0)
        self.assertNotEqual(post1.total_likes(), 1)

    def test_likes_count(self):
        post2 = Post.objects.get(pk=2)
        user1 = User.objects.get(pk=1)
        user2 = User.objects.get(pk=2)

        post2.likes.add(user1)
        self.assertEqual(post2.likes.all()[0], user1)
        # test a second like from same user
        post2.likes.add(user1)
        self.assertEqual(post2.likes.all()[0], user1)
        # add other likes and count
        post2.likes.add(user2)
        self.assertEqual(post2.likes.all().count(), 2)
        self.assertEqual(post2.likes.all()[1], user2)
        # remove like
        post2.likes.remove(user2)
        self.assertEqual(post2.likes.all().count(), 1)

    # POST VALIDATION
    def test_valid_post_length(self):
        p = Post.objects.get(pk=2)

        self.assertTrue(p.is_valid_post_length())

    def test_too_many_characters_in_post(self):
        p = Post.objects.get(pk=3)

        self.assertFalse(p.is_valid_post_length())

    def test_invalid_author(self):
        correct_user = User.objects.get(username="quigl")
        wrong_user = User.objects.get(username="bfly87")
        p = Post.objects.get(author=correct_user)

        self.assertNotEqual(p.author, wrong_user)
        self.assertEqual(p.author, correct_user)

    # FOLLOW USER
    def test_follow(self):
        user1 = User.objects.get(pk=1)
        user2 = User.objects.get(pk=2)

        def user_following_count(user):
            return user.following.all().count()
        # test nobody following
        self.assertEqual(user_following_count(user1), 0)
        # test follower
        user1.following.add(user2)
        self.assertEqual(user_following_count(user1), 1)
        # remove follower
        user1.following.remove(user2)
        self.assertEqual(user_following_count(user1), 0)

    # CLIENT TESTS

    # INDEX PAGE
    def test_index(self):
        c = Client()

        # store index request
        response = c.get("")
        posts = response.context["posts"]
        # ensure successful on loading index page
        self.assertEqual(response.status_code, 200)
        # make sure three posts returned
        self.assertEqual(len(posts), 3)
        # paginator
        self.assertEqual(posts.number, 1)
        self.assertEqual(posts.paginator.num_pages, 1)

    # PROFILE PAGE
    def test_profile(self):
        c = Client()
        user1 = User.objects.get(pk=1)
        response = c.get(f"/profile/{user1.username}")

        # test existing profile status code
        self.assertEqual(response.status_code, 200)

        # test non-existing profile status code
        response = c.get("/profile/dsjkad")
        self.assertEqual(response.status_code, 404)

        # test correct posts rendered on profile
        user2 = User.objects.get(pk=2)
        response = c.get(f"/profile/{user2.username}")
        posts = response.context["posts"]

        for post in posts:
            self.assertEqual(post.author, user2)

    # FOLLOWING PAGE
    def test_following_page(self):
        c = Client()
        user1 = User.objects.get(pk=1)
        user2 = User.objects.get(pk=2)
        # follow a user
        user1.following.add(user2)

        # test following page without logging in
        response = c.get('/following/True')
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)

        # test user logged in
        login = c.login(username=user1.username, password="testpass1")
        self.assertTrue(login)

        # login to view following page
        response = c.get('/following/True')
        self.assertEqual(response.status_code, 200)


# SELENIUM

class WebpageTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_index_title(self):
        self.driver.get(self.live_server_url)
        self.assertEqual(self.driver.title, "Social Network - All Posts")

    def test_login_title(self):
        self.driver.get(str(self.live_server_url + '/login'))
        self.assertEqual(self.driver.title, "Social Network - Login")

    def test_login_profile_page_and_like_button(self):
        # create test user and post
        user4 = User.objects.create(
            username="riqui", email="test@example.com", password="testpass1")
        post4 = Post.objects.create(author=user4, content="testing 1 2 1 2")

        force_login(user4, self.driver, self.live_server_url)
        self.driver.get(self.live_server_url)

        like = self.driver.find_element_by_id("2")
        like.click()
        time.sleep(1)
        self.assertEqual(like.text, "Unlike")
        post = Post.objects.get(pk=2)
        self.assertEqual(post.likes.all().count(), 1)
        self.driver.get(self.live_server_url + '/profile')

        self.assertEqual(self.driver.title, "Social Network - riqui")
        logout = self.driver.find_element_by_id("logout")
        logout.click()

    def test_follow_button_render(self):
        # create test users
        user5 = User.objects.create(
            username="hello", email="test@example.com", password="testpass1")
        user6 = User.objects.create(
            username="newuser", email="test@example.com", password="testpass1")

        # create test post
        post5 = Post.objects.create(
            author=user6, content="Are you following me?")

        # log user5 in

        force_login(user5, self.driver, self.live_server_url)

        self.driver.get(self.live_server_url)

        # go to new user profile and check follow button rendered on different profile
        user_profile_link = self.driver.find_elements_by_class_name(
            "card-title")
        user_profile_link[0].click()

        self.assertEqual(self.driver.title, "Social Network - newuser")
        follow_button = self.driver.find_element_by_id("follow")

        self.assertEqual(follow_button.text, "Follow")

        # logout
        logout = self.driver.find_element_by_id("logout")
        logout.click()
