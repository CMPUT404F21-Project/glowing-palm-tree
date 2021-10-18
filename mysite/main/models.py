from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.conf import settings

# Create your models here.

class User(AbstractUser):
    type = models.CharField(max_length=2000, null=True)
    uuid = models.CharField(max_length=2000, null=True)
    host = models.CharField(max_length=2000, null=True)
    displayName = models.CharField(max_length=2000, null=True)
    url = models.URLField(max_length=2000, null=True)
    github = models.URLField(max_length=2000, null=True)
    profileImage = models.URLField(max_length=2000, null=True)
    followList = models.JSONField(null=True)

    

class PostList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="postlist", null=True)
    name = models.CharField(max_length=2000)

    def __str__(self):
        return self.name

class Post(models.Model):
    postList = models.ForeignKey(PostList, on_delete=models.CASCADE)
    text = models.CharField(max_length=2000)
    complete = models.BooleanField()

    def __str__(self):
        return self.text