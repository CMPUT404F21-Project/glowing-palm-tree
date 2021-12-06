from django.contrib import admin
from .models import Following, Inbox, Liked, Likes, Moment, Comment, User, Pending
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.admin import TokenAdmin

TokenAdmin.raw_id_fields = ('user',)
# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Moment)
admin.site.register(Comment)
admin.site.register(Likes)
admin.site.register(Liked)
admin.site.register(Inbox)
admin.site.register(Pending)
admin.site.register(Following)
