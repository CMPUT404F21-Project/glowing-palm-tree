from django.http.response import HttpResponseForbidden, HttpResponseNotModified, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Inbox, Moment, Comment, Following, Likes, Liked
from django.forms.models import model_to_dict
from .forms import *
import datetime
from django.views.decorators.csrf import csrf_protect
import random
import json
from django.db import IntegrityError

# Create your views here.

def flat(arg):
    return arg[0]


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
    return render(response, "main/list.html", {"ls":ls})

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
    publicMoments = Moment.objects.filter(visibility__iexact="Public")
    selfMoments = response.user.moment.all()
    followerList = Following.objects.filter(following_user__exact=response.user).values_list('user',flat=True)
    followingList = Following.objects.filter(user__exact=response.user).values_list('following_user',flat=True)
    followerList = set(followerList)
    followingList = set(followerList)
    friendList = followerList.intersection(followingList)
    #print(friendList)

    #print(friendIdList)
    friendPost = Moment.objects.filter(user_id__in = friendList, visibility__in = ["Friend"] )
    print(friendPost)
    showList = publicMoments | selfMoments | friendPost

    return render(response, "main/view.html", {"showList":showList})

def userCenter(response, id):
    if(response.user.localId == id):
        return render(response, "main/userCenter.html", {"user":response.user})
    else:
        otherUser = User.objects.get(localId=id)
        user = response.user
        followList = Following.objects.filter(user__exact=user, following_user__exact=otherUser)
        following = followList.exists()
        return render(response, "main/otherUser.html", {"otherUser":otherUser, "following":following})

def userCenterEdit(response):
    if response.method == "POST":
        form = UserProfileEdit(response.POST, instance=response.user)
        if form.is_valid():
            #raise Exception         
            form.save()
            return HttpResponseRedirect("/author/%s" %response.user.localId)
    else:
        form = UserProfileEdit(instance=response.user)
        
    return render(response, "main/userCenterEdit.html", {"form":form})
  
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
            createdUser = form.save(commit=False)
            userId = response.build_absolute_uri('/author/') + createdUser.id
            host = response.build_absolute_uri('/')
            localId = createdUser.id
            createdUser.host = host
            createdUser.id = userId
            createdUser.url = userId
            createdUser.localId = localId
            print(userId)
            createdUser.save()

            initial_list = json.dumps([])
            
            inbox = Inbox.objects.create(author=createdUser, type="inbox",items = initial_list)
            inbox.save()
            return redirect("/login/")
        else:
            print(form.errors)
    else:
        form = RegisterForm()
    return render(response, "register/register.html", {"form":form})


def friendRequest(response, selfId, otherId):
    otherUser = User.objects.get(localId=otherId)
    try:
        Following.objects.create(user=response.user, following_user=otherUser)
    except IntegrityError:
        print("Already followed")

    return HttpResponseRedirect("/author/%s" %otherId)

def unfollow(response, otherId):
    otherUser = User.objects.get(localId=otherId)
    user =  response.user
    quertSet = Following.objects.filter(user__exact=user, following_user__exact=otherUser)
    if quertSet.exists():
        quertSet.delete()
    
    return HttpResponseRedirect("/author/%s" %otherId)

def inbox(response, id):
    
    
    if(response.method == "POST"):
        object = response.POST.get("like")    
        moment = Moment.objects.get(id=int(object))
        object = response.POST.get("like")
        
        moment = Moment.objects.get(id=int(object))
        
        selfName = response.user.username
        summary = "%s likes your Post(title: %s)"%(selfName, moment.title)
        author = moment.user.url

        url = author+'/post/' + object

        host = response.build_absolute_uri('/')
        url.replace(host, "")

        print(url)
        print("hhhhhhh")
        like = Likes.objects.create(object=url, type="Like", author=moment.user.id, summary=summary)

        inbox = Inbox.objects.get(author=moment.user)
        
        items = inbox.items
        
        items = json.loads(items)

        dict_object = model_to_dict(like)
        #print(dict_object)

        items.append(dict_object)

        items = json.dumps(items)

        inbox.items = items
        inbox.save()
        #json_object = json.dumps(dict_object)
        #inbox.items.
        return HttpResponseRedirect("/%i" %moment.id)
    else:
        inbox = Inbox.objects.get(author=response.user)
        items = inbox.items
        items = json.loads(items)
            
        return render(response, "main/messageBox.html", {"items":items})

    


    
