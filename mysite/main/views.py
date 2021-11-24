from django.http.response import HttpResponseForbidden, HttpResponseNotModified, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, request
from .models import Inbox, Moment, Comment, Following, Likes, Liked, User
from django.forms.models import model_to_dict
from django.core import serializers
from .forms import *
import datetime
from django.views.decorators.csrf import csrf_protect
import random
import json
from django.db import IntegrityError
from uuid import uuid4
import math
from urllib.parse import urlparse
from django.template.loader import render_to_string

# Create your views here.

def flat(arg):
    return arg[0]



def doMoment(response, authorId):
    # ls = Moment.objects.filter(id__exact=postId)
    #if(not ls.exists()):
    if response.method == "POST":
        if authorId == response.user.localId:
            form = CreateNewMoment(response.POST)
            if form.is_valid():
                #raise Exception
                p = form.save(commit=False)
                postId = str(uuid4())
                p.id = response.build_absolute_uri() + postId
                print("ggggggaaaaaaaaaaa")
                print(p.id)
                p.user = response.user
                p.published = datetime.datetime.now()
                p.save()
                response.user.moment.add(p)
                # p = serializers.serialize('json', [p,])
                # p = json.loads(p)[0]
                # p = json.dumps(p)
                content = p.content
                contentType = p.contentType
                return render(response, "main/list.html", {"ls":p, "content":content, "contentType": contentType})
    else:
        user = User.objects.get(localId=authorId)
        # ls = Moment.objects.filter(user__exact=user).order_by("-published")


        publicMoments = Moment.objects.filter(visibility__iexact="Public", user__exact=user)
        # selfMoments = response.user.moment.all()
        followerList = Following.objects.filter(following_user__exact=user, user__exact=response.user)
        followingList = Following.objects.filter(user__exact=user, following_user__exact=response.user)
        # followerList = set(followerList)
        # followingList = set(followingList)
        # friendList = followerList.intersection(followingList)
        
        showListFull = publicMoments
        if followerList.exists() and followingList.exists():
            friendMoments = Moment.objects.filter(visibility__iexact="Friend", user__exact=user)
            showListFull = publicMoments.union(friendMoments)

        # friendPost = Moment.objects.filter(user_id__in = friendList, visibility__in = ["Friend"] )
        # showList = publicMoments.union(ls).union(friendPost)
        content = showListFull.values_list('content', flat=True)
        
        page =  int(response.GET.get("page", 1))
        size =  int(response.GET.get("size", 5))
        
        
        btType = response.GET.get("type", '')

        # if(btType == "next"):
        #     page = page + 1
        # elif(btType == "previous"):
        #     page = page - 1

        # print(page)
        # print(size)
        # print("here is")

        offset = (page-1)*size
        lsList = list(showListFull)
        contentList = list(content)
        showList = []
        showContent = []

        if(len(lsList) >= (offset+size) ):
            showList = lsList[offset:(offset+size)]
            showContent = contentList[offset:(offset+size)]

        else:
            if(len(lsList) > offset):
                showList = lsList[offset:]
                showContent = contentList[offset:]

        maxPage = math.ceil(len(lsList)/size)
        showContent = json.dumps(showContent)

        return render(response, "main/aPostList.html", {"authorId":authorId,"showList":showList, "size":size, "page": page, "maxPage":maxPage, "content":showContent})
        

def userMoment(response, authorId, postId):
    #url = "http://localhost:8000/" + "author/" + authorId + "/posts/" + postId
    url = urlparse(response.build_absolute_uri())
    cleanUrl = response.build_absolute_uri().replace("?" + url.query,'')
    print(cleanUrl)
    ls = Moment.objects.filter(id__exact=cleanUrl )
    ls = ls[0]
    '''if response.method == "POST":
        # print(response.POST)
        if response.POST.get("newComment"):
            txt = response.POST.get("new")
            if len(txt) > 2:
                ls.comment_set.create(content=txt, published=datetime.datetime.now(), complete=False)
            else:
                print("invalid")'''
    if response.method == "GET":
        like = Likes.objects.filter(userId__exact=response.user.id, object__exact=ls.id)
        content = ls.content
        return render(response, "main/list.html", {"ls":ls, 'liked':(like.exists()), 'content':content})
    elif response.method == "POST":
        if(response.POST.get("_METHOD") == "Delete"):
            ls.delete()
            showList = Moment.objects.filter(user__exact=response.user).order_by("-published")
            content = list(showList.values_list('content', flat=True))
            content = json.dumps(content)
            return render(response, "main/userCenter.html", {"user":response.user,"showList":showList, "content":content})
        else:
            form = CreateNewMoment(response.POST, instance=ls)
            if form.is_valid():
                #raise Exception         
                form.save()
                content = str(form.cleaned_data.get('content')) 
                return render(response, "main/list.html", {"ls":ls, 'content':content})

    elif response.method == "DELETE":
        ls.delete()
        return HttpResponseRedirect("/author/%s/posts/%s" %(authorId, postId))

    return render(response, "main/list.html", {"ls":ls})

def home(response):
    moments = Moment.objects.filter(visibility__iexact="Public")
    moments = moments.order_by("-published")
    content = list(moments.values_list('content', flat=True))
    
    content = json.dumps(content)
    form = CreateNewMoment()
    return render(response, "main/home.html", {"form":form, "moments":moments, "content":content})


def view(response):
    publicMoments = Moment.objects.filter(visibility__iexact="Public")
    selfMoments = response.user.moment.all()
    followerList = Following.objects.filter(following_user__exact=response.user).values_list('user',flat=True)
    followingList = Following.objects.filter(user__exact=response.user).values_list('following_user',flat=True)
    followerList = set(followerList)
    followingList = set(followingList)
    friendList = followerList.intersection(followingList)
    #print(friendList)

    #print(friendIdList)
    friendPost = Moment.objects.filter(user_id__in = friendList, visibility__in = ["Friend"] )
    showList = publicMoments.union(selfMoments).union(friendPost)
    showList = showList.order_by('-published')
    content = list(showList.values_list('content', flat=True))
    content = json.dumps(content)

    return render(response, "main/view.html", {"showList":showList, 'user':response.user, 'content':content})

def userCenter(response, id):
    if(response.user.localId == id):
        showList = Moment.objects.filter(user__exact=response.user).order_by("-published")
        content = list(showList.values_list('content', flat=True))
        content = json.dumps(content)
        return render(response, "main/userCenter.html", {"user":response.user,"showList":showList, "content":content},)
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
    # maybe like maybe share
    if(response.method == "POST"):
        type = response.POST.get("like", "")
        url = response.POST.get("url", "")
        moment = Moment.objects.get(id=url)
        selfName = response.user.username
        
        
        if(type == "like"):
            print("hahahahaha")
            inbox = Inbox.objects.get(author=moment.user)
            user = serializers.serialize("json", [moment.user,])
            user = json.loads(user)[0]
            user = json.dumps(user)
            summary = "%s likes your Post(title: %s)"%(selfName, moment.title)
            like = Likes.objects.create(object=url, type="Like", author=user , summary=summary, userId=response.user.id)
            dict_object = model_to_dict(like)
        else:
            
            dict_object = model_to_dict(moment)
        #print(dict_object)
        items = inbox.items
        items = json.loads(items)
        items.append(dict_object)
        items = json.dumps(items)
        inbox.items = items
        inbox.save()
        return HttpResponseRedirect(url)
    else:
        inbox = Inbox.objects.get(author=response.user)
        items = inbox.items
        items = json.loads(items)
            
        return render(response, "main/messageBox.html", {"items":items})


def momentEdit(response,authorId, postId):
    postId = response.build_absolute_uri().replace('/edit', '')
    ls = Moment.objects.filter(id__exact=postId )
    ls = ls[0]
    content = str(ls.content)
    ls.content = ''
    form = CreateNewMoment(instance=ls)    
    return render(response, "main/momentEdit.html", {"form":form, "pl":ls, 'content':content})


def createComment(response, authorId, postId):
    momentUrl = response.build_absolute_uri()
    momentUrl = momentUrl.replace("/comments", "")
    print(momentUrl)
    moment = Moment.objects.get(id=momentUrl)
    commentUuid = str(uuid4())
    comment = Comment.objects.create()
    comment.commentId = response.build_absolute_uri() + "/" + commentUuid
    comment.moment = moment
    print("outside")
    if response.method == "POST":
        print("enter")
        comment.content = response.POST.get("content")
        comment.author = response.user
        comment.type = "comment"
        comment.published = datetime.datetime.now()
        comment.save()
    url = response.POST.get("url")
    return HttpResponseRedirect(url)

def momentShare(response, authorId, postId):
    print("1")
    url = response.build_absolute_uri().replace("/share", "")
    ls = Moment.objects.filter(id__exact=url)
    user = User.objects.filter(localId__exact=authorId)
    ls = ls[0]
    user = user[0]
    uuid = str(uuid4())
    newId = response.user.id + "/posts/" + uuid
    #print(user)
    #print(ls)
    newLs = Moment.objects.create(id=newId, content=ls.content, contentType=ls.contentType, user=response.user,
                                    source=user.id, published=datetime.datetime.now(), title=ls.title,visibility=ls.visibility )

    # newLs.content = ls.content
    # newLs.contenType = ls.contentType
    # newLs.user = response.user
    # newLs.source = user.id
    # newLs.published = datetime.datetime.now()
    newLs.save()
    content = ls.content
    contentType = ls.contentType
    
    return render(response, "main/list.html", {"ls":newLs, "content":content, "contentType": contentType}) 


def getFriend(response):

    followerList = Following.objects.filter(following_user__exact=response.user).values_list('user',flat=True)
    followingList = Following.objects.filter(user__exact=response.user).values_list('following_user',flat=True)
    friendList = list(followerList.intersection(followingList))

    friendList = User.objects.filter(id__in=friendList)
    

    friendListName = list(friendList.values_list("username",flat=True))
    friendListId = list(friendList.values_list("id", flat=True))

    nameListJs = json.dumps(friendListName)
    idListJs = json.dumps(friendListId)

    return JsonResponse({"nameList":nameListJs, "idList":idListJs})


# def getForm(response, formType):
#     if formType == "file":
#         form = CreateNewImageMoment()
#     else:
#         form = CreateNewMoment()
#     renderHtml = render_to_string("main/home.html", {"form": form})
#     print(renderHtml)
#     return JsonResponse({"form":renderHtml})
    
