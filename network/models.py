from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField(
        "self", symmetrical=False, blank=True, default=None)

    def total_following(self):
        return self.following.count()


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        User, blank=True, default=None, related_name="post_likes")

    def total_likes(self):
        return self.likes.count()

    def is_valid_post_length(self):
        return len(self.content) < 251

    def __str__(self):
        return f"post {self.id}: {self.author} said: {self.content[0:15]}... on {self.date}."
