from django.urls import path
from django.urls.resolvers import URLPattern
from . import views, service

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
    path("author/<str:authorId>/posts/<str:postId>/share", views.momentRepost, name = "momentRepost"),
    path("getFriend/", views.getFriend, name = "getFriend"),
    # path("get/form/<str:formType>", views.getForm, name="getForm")


    # GET: retrieve all profiles on the server paginated
    path("service/authors/", service.retrive_user_all, name="retrive_user_all"), 

    # GET: retrieve their profile
    # POST: update profile
    path("service/author/<str:author_id>/", service.retrive_user, name="retrive_user"),
    
    # GET: get a list of authors who are their followers
    path("service/author/<str:author_id>/followers", service.retrive_followers, name="retrive_followers"),
    
    # DELETE: remove a follower
    # PUT: Add a follower (must be authenticated)
    # GET check if follower
    path("service/author/<str:author_id>/followers/<str:foreign_author_id>", service.manage_followers, name="manage_followers"),

    # GET get the public post
    # POST update the post (must be authenticated)
    # DELETE remove the post
    # PUT create a post with that post_id
    path("service/author/<str:author_id>/posts/<str:post_id>", service.manage_posts, name="manage_posts"),

]