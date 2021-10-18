from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import PostList, Post
from .forms import CreateNewPostList
from .forms import RegisterForm
from django.views.decorators.csrf import csrf_protect
# Create your views here.

def index(response, id):
    ls = PostList.objects.get(id=id)
    if ls in response.user.postlist.all():
        if response.method == "POST" :
            # print(response.POST)
            if response.POST.get("save"):
                for post in ls.post_set.all():
                    if response.POST.get("c"+ str(post.id)) == "clicked":
                        post.complete = True
                    else:
                        post.complete = False
                    post.save()
            elif response.POST.get("newPost"):
                txt = response.POST.get("new")
                if len(txt) > 2:
                    ls.post_set.create(text=txt, complete=False)
                else:
                    print("invalid")

        return render(response, "main/list.html", {"ls":ls})
    return render(response, "main/view.html", {})

def home(response):
    return render(response, "main/home.html", {})

def create(response):
    if response.method == "POST":
        form = CreateNewPostList(response.POST)
        if form.is_valid():
            n = form.cleaned_data["name"]
            p = PostList(name=n)
            p.save()
            response.user.postlist.add(p)

        return HttpResponseRedirect("/%i" %p.id)
    else:
        form = CreateNewPostList()
    return render(response, "main/create.html", {"form":form})

def view(response):
    return render(response, "main/view.html", {})

@csrf_protect
def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
        else:
            print(form.errors)
    else:
        form = RegisterForm()
    return render(response, "register/register.html", {"form":form})