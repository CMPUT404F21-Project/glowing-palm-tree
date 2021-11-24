from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns = [
    path("author/<str:authorId>/posts/<str:postId>", views.userMoment, name = "userMoment"),
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
    path("momentEdit/<str:postId>", views.momentEdit, name="MomentEdit"),
    path("author/<str:authorId>/posts/", views.doMoment, name = "doMoment"),
    path("author/<str:authorId>/posts/<str:postId>/comments", views.createComment, name = "createComment"),
    path("author/<str:authorId>/posts/<str:postId>/edit", views.momentEdit, name = "momentEdit"),
    path("author/<str:authorId>/posts/<str:postId>/share", views.momentShare, name = "momentShare"),
    path("getFriend/", views.getFriend, name = "getFriend")
    # path("get/form/<str:formType>", views.getForm, name="getForm")
]