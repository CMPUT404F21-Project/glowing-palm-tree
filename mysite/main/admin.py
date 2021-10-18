from django.contrib import admin
from .models import PostList, Post, User
from django.contrib.auth.admin import UserAdmin
# Register your models here.
admin.site.register(PostList)
admin.site.register(Post)
admin.site.register(User, UserAdmin)
