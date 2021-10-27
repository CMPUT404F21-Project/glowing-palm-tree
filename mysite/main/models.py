from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.conf import settings

# Create your models here.

class User(AbstractUser):
    type = models.CharField(max_length=2000, null=True)
    userId = models.CharField(max_length=2000, null=True)
    host = models.CharField(max_length=2000, null=True)
    displayName = models.CharField(max_length=2000, null=True)
    url = models.URLField(max_length=2000, null=True)
    github = models.URLField(max_length=2000, null=True)
    profileImage = models.URLField(max_length=2000, null=True)
    followList = models.JSONField(null=True)

    

class Moment(models.Model):
    type = models.CharField(max_length=2000, null=True)
    title = models.CharField(max_length=2000, null=True)
    momentId = models.CharField(max_length=2000, null=True)
    source = models.CharField(max_length=2000, null=True)
    origin = models.CharField(max_length=2000, null=True)
    description = models.CharField(max_length=2000, null=True)
    contentTyep = models.CharField(max_length=2000, null=True)
    content = models.CharField(max_length=2000, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="moment", null=True)
    categories = models.JSONField(null=True)
    count = models.PositiveIntegerField(null=True)
    comments = models.URLField(null=True)
    commentsSrc = models.JSONField(null=True)
    published = models.DateTimeField(null=True)
    visibility = models.CharField(max_length=2000,null=True)
    unlisted = models.BooleanField(null=True)

    def __str__(self):
        return self.content

class Comment(models.Model):
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=2000, null=True)
    author =  models.JSONField(null=True)
    content = models.CharField(max_length=2000, null=True)
    contentType = models.CharField(max_length=2000, null=True)
    published = models.DateTimeField(null=True)
    commentId = models.CharField(max_length=2000, null=True)
    
    complete = models.BooleanField(null=True)

    def __str__(self):
        return self.content


class Likes(models.Model):
    context = models.URLField()
    summary = models.CharField(max_length=2000)
    type = models.CharField(max_length=2000)
    author = models.JSONField()
    object = models.URLField()

class Liked(models.Model):
    type = models.CharField(max_length=2000)
    itmes = models.JSONField()

class Inbox(models.Model):
    type = models.CharField(max_length=2000)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inbox", null=True)
    items = models.JSONField()
