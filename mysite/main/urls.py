from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns = [
    path("<int:id>", views.index, name = "index"),
    path("home/", views.home, name = "home"),
    path("create/", views.home, name = "create"),
    path("view/", views.view, name="view"),
    path("register/", views.register, name="register"),
    path("author/<str:id>", views.userCenter, name="userCenter"),
    path("messageBox/", views.messageBox, name="messageBox"),
    path("following/", views.following, name="following"),
    path("userCenterEdit/", views.userCenterEdit, name="userCenterEdit"),
    path("friendRequest/<str:selfId>/<str:otherId>", views.friendRequest, name="friendRequest"),
    path("unfollow/<str:otherId>", views.unfollow, name="unfollow"),
    path("author/<str:id>/inbox/", views.inbox, name="inbox"),
]