from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns = [
    path("<int:id>", views.index, name = "index"),
    path("", views.home, name = "home"),
    path("create/", views.home, name = "create"),
    path("view/", views.view, name="view"),
    path("register/", views.register, name="register"),
]