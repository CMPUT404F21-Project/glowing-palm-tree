from django.contrib import admin
from .models import Inbox, Liked, Likes, Moment, Comment, User
from django.contrib.auth.admin import UserAdmin
# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Moment)
admin.site.register(Comment)
admin.site.register(Likes)
admin.site.register(Liked)
admin.site.register(Inbox)
