from django.http.response import HttpResponseForbidden, HttpResponseNotModified, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Moment, Comment, Following
from .forms import *
import datetime
from django.views.decorators.csrf import csrf_protect
import random
import json
from django.db import IntegrityError
# Create your views here.

def index(response, id):
    ls = Moment.objects.get(id=id)
    if ls in response.user.moment.all():
        if response.method == "POST" :
            # print(response.POST)
            if response.POST.get("newComment"):
                txt = response.POST.get("new")
                if len(txt) > 2:
                    ls.comment_set.create(content=txt, published=datetime.datetime.now(), complete=False)
                else:
                    print("invalid")

        return render(response, "main/list.html", {"ls":ls})
    return render(response, "main/view.html", {})

def home(response):
    moments = Moment.objects.filter(visibility__iexact="Public")
    if response.method == "POST":
        form = CreateNewMoment(response.POST)
        if form.is_valid():
            #raise Exception
            n = form.cleaned_data["content"]
            t = form.cleaned_data["title"]
            v = form.cleaned_data["visibility"]
            p = Moment(content=n, title=t,visibility=v,published=datetime.datetime.now())
            p.save()
            response.user.moment.add(p)
            return HttpResponseRedirect("/%i" %p.id)
        else:
            print(form.errors)
    else:
        form = CreateNewMoment()
    return render(response, "main/home.html", {"form":form, "moments":moments})


def view(response):
    return render(response, "main/view.html", {})

def userCenter(response):
    user = response.user

    return render(response, "main/userCenter.html", {"user":user})

def userCenterEdit(response):
    if response.method == "POST":
        form = UserProfileEdit(response.POST, instance=response.user)
        if form.is_valid():
            #raise Exception         
            form.save()
            return HttpResponseRedirect("/userCenter/")
    else:
        form = UserProfileEdit(instance=response.user)
        
    return render(response, "main/userCenterEdit.html", {"form":form})


def otherUser(response,id):
    if(response.user.id == id):
        return HttpResponseRedirect("/userCenter/")
    otherUser = User.objects.get(id=id)
    user = response.user
    followList = Following.objects.filter(user_id__exact=user, following_user_id__exact=otherUser)
    following = followList.exists()

    return render(response, "main/otherUser.html", {"otherUser":otherUser, "following":following})

def messageBox(response):
    user = response.user
    return render(response, "main/messageBox.html", {"user":user})

def following(response):
    user = response.user
    return render(response, "main/following.html", {"user":user})

@csrf_protect
def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            return redirect("/login/")
        else:
            print(form.errors)
    else:
        form = RegisterForm()
    return render(response, "register/register.html", {"form":form})


def friendRequest(response, selfId, otherId):
    otherUser = User.objects.get(id=otherId)
    try:
        Following.objects.create(user_id=response.user, following_user_id=otherUser)
    except IntegrityError:
        print("Already followed")

    return HttpResponseRedirect("/otherUser/%i" %otherId)

def unfollow(response, otherId):
    otherUser = User.objects.get(id=otherId)
    user =  response.user
    quertSet = Following.objects.filter(user_id__exact=user, following_user_id__exact=otherUser)
    if quertSet.exists():
        quertSet.delete()
    
    return HttpResponseRedirect("/otherUser/%i" %otherId)

    
