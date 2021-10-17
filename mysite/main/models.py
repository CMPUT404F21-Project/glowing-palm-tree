from django.db import models
from django.contrib.auth.models import User

# Create your models here.

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