# from _typeshed import OpenTextModeWriting
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseNotModified, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, request
from datetime import datetime
from main.views import following
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

def send_to_inbox(item, inboxes):
    for inbox in inboxes:
        items = inbox.items
        items = json.loads(items)
        items.append(item)
        items = json.dumps(items, default=date_converter)
        inbox.items = items
        inbox.save()
    return

def get_friends(user):
    followerList = Following.objects.filter(following_user__exact=user).values_list('user',flat=True)
    followingList = Following.objects.filter(user__exact=user).values_list('following_user',flat=True)

    friendList = followerList.intersection(followingList)
    return friendList


def date_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def retrive_user_all(response):
    if response.method != "GET":
        return HttpResponseNotAllowed()
    users = list(User.objects.all())
    page  = response.GET.get("page", 1)
    size = response.GET.get("size", len(users))
    offset = (page-1)*size

    if(len(users) >= (offset+size) ):
            users = users[offset:(offset+size)]
    else:
        if(len(users) > offset):
            users = users[offset:]
        else:
            users = []

    json_response = {
        "type": "authors",
        "data": [],
        }
    for user in users:
        user_object = {
            "type": "author",
            "id": user.id,
            "url": user.url,
            "host": user.host,
            "displayName": user.username,
            "github":user.github,
            "profileImage": user.profileImage
        }
        json_response["data"].append(user_object)

    return JsonResponse(json_response)

def retrive_user(response, author_id):
    if response.method == "GET":
        
        user = get_object_or_404(User, localId=author_id)
        
        json_response = {
                "type": "author",
                "data":[
                    {
                        "type" : "author",
                        "id": user.id,
                        "url": user.url,
                        "host": user.host,
                        "displayName": user.username,
                        "github":user.github,
                        "profileImage": user.profileImage
                    }
                ]
            }
        return JsonResponse(json_response)
    elif response.method == "POST":
        user = get_object_or_404(User, localId=author_id)

        form = UserProfileEdit(response.POST, instance=user)
        if form.is_valid:
            form.save()
        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed()

def retrive_followers(response, author_id):
    if response.method != "GET":
        return HttpResponseNotAllowed()
    user = get_object_or_404(User, localId=author_id)
    followers = Following.objects.filter(following_user__exact=user.id).values_list("user")
    followers = User.objects.filter(id__in=followers)

    json_response = {
        "type": "followers",
        "data": [],
        }
    for user in followers:
        user_object = {
            "type": "author",
            "id": user.id,
            "url": user.url,
            "host": user.host,
            "displayName": user.username,
            "github":user.github,
            "profileImage": user.profileImage
        }
        json_response["data"].append(user_object)
    return JsonResponse(json_response)

def manage_followers(response, author_id, foreign_author_id):
    user = get_object_or_404(User, localId=author_id)
    if response.method == "GET":
        follower = Following.objects.filter(user__exaxt=user.id, following_user__exact=foreign_author_id)
        if follower.exists():
            return JsonResponse({"follower":True})
        else:
            return JsonResponse({"follower":False})

    elif response.method == "PUT":
        type = response.data["type"]
        if not type == "follower":
            return HttpResponseBadRequest("Data must be of type 'follower'.")
        data = response.data["data"][0]
        foreign_user_id = data["id"]

        
        following = Following.objects.create(user=user.id, following_user=foreign_user_id)
        following.save()
        return HttpResponse(status=204)

    elif response.method == "DELETE":
        following = Following.objects.filter(user__exact=user.id, following_user__contains=foreign_author_id)
        if not following.exists():
            return HttpResponseNotFound("No such follower")
        following[0].delete()
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed()

def manage_posts(response, author_id, post_id):
    if response.method == "GET":
        # url = response.build_absolute_uri()
        # url = url.replace("/service", "")
        # request_host = response.get_host()
        # url = url.replace(request_host, "127.0.0.1")
        ls = get_object_or_404(Moment, localId=post_id)
        user = ls.user
        json_response = {
            "type": "posts",
            "data":[]
        }
        obj = {
            "type": "post",
            "title": ls.title,
            "id": ls.id,
            "source": ls.source,
            "origin": ls.origin,
            "description": ls.description,
            "contentType": ls.contentType,
            "content": ls.content,
            "author": {
                "type": "author",
                "id": user.id,
                "url": user.url,
                "host": user.host,
                "displayName": user.username,
                "github":user.github,
                "profileImage": user.profileImage
            },
            "categories": ls.categories,
            "counts": ls.count,
            "comments": ls.id,
            "commentsSrc": None,
            "published": ls.published.__str__(),
            "visibility": ls.visibility,
            "unlisted": ls.unlisted
        }
        json_response["data"].append(obj)
        return JsonResponse(json_response)

    elif response.method == "POST":
        ls = get_object_or_404(Moment, localId=post_id)
        data = response.data["data"][0]
        for key in data:
            setattr(ls, key, data[key])
        try:
            ls.save()
            return HttpResponse(status=204)
        except:
            return HttpResponseBadRequest("Can not parse some of the fields")

    elif response.method == "DELETE":
        ls = get_object_or_404(Moment, localId=post_id)
        ls.delete()
        return HttpResponse(status=204)
    elif response.methid == "PUT":
        data = response.data["data"]
        for ls in data:
            moment = Moment.objects.create(type="post", title=ls["title"], id=ls["id"], localId=post_id,
                                            source=ls["source"], origin=ls["origin"], description=ls["description"],
                                            contentType=ls["contentType"], content=ls["content"], categories=ls["categories"],
                                            counts=ls["counts"], comments=ls["comments"], commentsSrc=ls["commentsSrc"],
                                            published=datetime.strptime(ls["published"], '%H:%M:%S').time(), visibility=ls["visibility"], unlisted=ls["unlisted"]
            )
        try:
            moment.save()
            return HttpResponse(204)
        except:
            return HttpResponseBadRequest("Can not parse some of the fields")
    else:
        return HttpResponseNotAllowed()
    
def do_posts(response, author_id):
    if response.method == "POST":
        form = CreateNewMoment(response.POST)
        if form.is_valid():
            #raise Exception
            p = form.save(commit=False)
            postId = str(uuid4())
            p.id = response.build_absolute_uri() + postId
            p.type = 'post'
            p.source = p.id
            p.origin = p.id
            p.count = 0
            # p.comment = ""

            p.user = response.user
            p.published = datetime.datetime.now()
            p.save()
            response.user.moment.add(p)

            if p.visibility in ["Public", "Friend"]:
                friend_list = get_friends(response.user)
                inboxes = Inbox.objects.filter(author__in=friend_list)
                dict_object = model_to_dict(p)
                dict_object['user'] = response.user.username
                dict_object['userLink'] = response.user.id
                send_to_inbox(dict_object, list(inboxes))
    elif response.method == "GET":
        user = get_object_or_404(User, localId=author_id)
        moments = list(Moment.objects.filter(user__exact=user.id).order_by("-published"))

        page  = response.GET.get("page", 1)
        size = response.GET.get("size", len(moments))
        offset = (page-1)*size

        if(len(moments) >= (offset+size) ):
                moments = moments[offset:(offset+size)]
        else:
            if(len(moments) > offset):
                moments = moments[offset:]
            else:
                moments = []


        json_response = {
            "type": "post",
            "data": []
        }

        for ls in moments:
            moment = {
                "type": "post",
                "title": ls.title,
                "id": ls.id,
                "source": ls.source,
                "origin": ls.origin,
                "description": ls.description,
                "contentType": ls.contentType,
                "content": ls.content,
                "author": {
                    "type": "author",
                    "id": user.id,
                    "url": user.url,
                    "host": user.host,
                    "displayName": user.username,
                    "github":user.github,
                    "profileImage": user.profileImage
                    },
                "categories": ls.categories,
                "counts": ls.count,
                "comments": ls.comments,
                "commentsSrc": None,
                "published": ls.published.__str__(),
                "visibility": ls.visibility,
                "unlisted": ls.unlisted
                }
            json_response["data"].append(moment)

        return JsonResponse(json_response)

def manage_comments(response, author_id, post_id):
    moment = get_object_or_404(Moment, localId=post_id)
    if response.method == "GET":
        user = User.objects.get(id=moment.user.id)
        comments = list(Comment.objects.filter(moment__exact=moment.id))

        page  = response.GET.get("page", 1)
        size = response.GET.get("size", len(comments))
        offset = (page-1)*size

        if(len(comments) >= (offset+size) ):
                comments = comments[offset:(offset+size)]
        else:
            if(len(comments) > offset):
                comments = comments[offset:]
            else:
                comments = []


        json_response = {
            "type":"comments",
            "data":[]
        }

        for comment in comments:
            obj = {
                "type": "comment",
                "author":{
                    "type": "author",
                    "id": user.id,
                    "url": user.url,
                    "host": user.host,
                    "displayName": user.username,
                    "github": user.github,
                    "profileImage": user.profileImage
                },
                "comment":comment.content,
                "contentType":comment.contentType,
                "published": comment.published.__str__(),
                "id": comment.commentId
            }
            json_response["data"].append(obj)

        return JsonResponse(json_response)
    elif response.method == "POST":
        obj_type = response.data["type"]
        if not obj_type == "comment":
            return HttpResponseBadRequest
        data = response.data["data"]
        comment = Comment.objects.create(commentId=str(uuid4()), moment=moment.id, type="comment", user=data["author"]["id"], 
                                            content=data["comment"], contentType=data["contentType"], published=data["published"]
                                        )
        comment.save()
    else:
        return HttpResponseNotAllowed

def send_inbox(response, author_id):
    user = get_object_or_404(User, localId=author_id)
    inbox = Inbox.objects.get(author=user.id)
    if response.method == "POST":
        data = response.data
        if data["type"] == "like":
            like = Likes.objects.create(type="like", summary=data["summary"], author=data["author"], object=data["object"])
            like.save()
            send_to_inbox(like, [inbox])
            return HttpResponse(status=201)
        elif data["type"] == "post":
            moment = data["data"]
            moment["user"] = moment["author"]["displayName"]
            moment["userLink"] = "foreign"
            send_to_inbox(moment, [inbox])
        elif data["type"] == "follow":
            userId = data["data"]["object"]["id"]
            follower = data["data"]["actor"]["id"]
            inbox = get_object_or_404(Inbox, author=userId)
            following = Following.objects.create(user=follower, following_user=follower)
            following.save()
            following = model_to_dict(following)
            send_to_inbox(following, [inbox])
        else:
            return HttpResponseBadRequest
    elif response.method == "GET":
        items = inbox.items
        items = json.loads(items)
        json_response = {
            "type": "posts",
            "data":[]
        }

        for item in items:
            if item["type"] == "post":
                json_response["data"].append(item)

        return JsonResponse(json_response)
    
    elif response.method == "DELETE":
        inbox.items = json.dumps([])
        inbox.save()
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed

def get_likes_post(response, author_id, post_id):
    user = get_object_or_404(User, localId=author_id)
    moment = get_object_or_404(Moment, localId=post_id, user=user.id)
    
    if response.method == "GET":
        likes = Likes.objects.filter(object__exact=moment.id).exclude(userId__exact=user.id)

        page  = response.GET.get("page", 1)
        size = response.GET.get("size", len(likes))
        offset = (page-1)*size

        if(len(likes) >= (offset+size) ):
                likes = likes[offset:(offset+size)]
        else:
            if(len(likes) > offset):
                likes = likes[offset:]
            else:
                likes = []


        json_response = {
            "type": "likes",
            "data":[]
        }

        for like in likes:
            userId = like.userId
            if userId:
                user = User.objects.get(id=userId)
                obj = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "summary": like.summary,
                "author":{
                    "type": "author",
                    "id": user.id,
                    "url": user.url,
                    "host": user.host,
                    "displayName": user.username,
                    "github": user.github,
                    "profileImage": user.profileImage
                },
                "object": like.object
            }
            else:
                user = like.author
                obj = {
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "summary": like.summary,
                    "author":{
                        "type": "author",
                        "id": user["id"],
                        "url": user["url"],
                        "host": user["host"],
                        "displayName": user["diaplayName"],
                        "github": user["github"],
                        "profileImage": user["profileImage"]
                    },
                    "object": like.object
                }
            json_response["data"].append(obj)
        
        return JsonResponse(json_response)
    else:
        return HttpResponseNotAllowed

def get_likes_comment(response, author_id, post_id, comment_id):
    user = get_object_or_404(User, localId=author_id)
    moment = get_object_or_404(Moment, localId=post_id, user=user.id)
    comment = get_object_or_404(Comment, localId=comment_id, moment=moment.id)
    
    if response.method == "GET":
        likes = Likes.objects.filter(object__exact=comment.id).exclude(userId__exact=user.id)

        page  = response.GET.get("page", 1)
        size = response.GET.get("size", len(likes))
        offset = (page-1)*size

        if(len(likes) >= (offset+size) ):
                likes = likes[offset:(offset+size)]
        else:
            if(len(likes) > offset):
                likes = likes[offset:]
            else:
                likes = []

        json_response = {
            "type": "likes",
            "data":[]
        }
        for like in likes:
            userId = like.userId
            if userId:
                user = User.objects.get(id=userId)
                obj = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "summary": like.summary,
                "author":{
                    "type": "author",
                    "id": user.id,
                    "url": user.url,
                    "host": user.host,
                    "displayName": user.username,
                    "github": user.github,
                    "profileImage": user.profileImage
                },
                "object": like.object
            }
            else:
                user = like.author
                obj = {
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "summary": like.summary,
                    "author":{
                        "type": "author",
                        "id": user["id"],
                        "url": user["url"],
                        "host": user["host"],
                        "displayName": user["diaplayName"],
                        "github": user["github"],
                        "profileImage": user["profileImage"]
                    },
                    "object": like.object
                }
            json_response["data"].append(obj)
        return JsonResponse(json_response)
    else:
        return HttpResponseNotAllowed

def get_liked(response, author_id):
    user = get_object_or_404(User, localId=author_id)
    if response.method == "GET":
        likes = Likes.objects.filter(userId__exact=user.id)
        
        page  = response.GET.get("page", 1)
        size = response.GET.get("size", len(likes))
        offset = (page-1)*size

        if(len(likes) >= (offset+size) ):
                likes = likes[offset:(offset+size)]
        else:
            if(len(likes) > offset):
                likes = likes[offset:]
            else:
                likes = []
        json_response = {
            "type": "liked",
            "data":[]
        }
        for like in likes:
            userId = like.userId
            if userId:
                user = User.objects.get(id=userId)
                obj = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "summary": like.summary,
                "author":{
                    "type": "author",
                    "id": user.id,
                    "url": user.url,
                    "host": user.host,
                    "displayName": user.username,
                    "github": user.github,
                    "profileImage": user.profileImage
                },
                "object": like.object
            }
            else:
                user = like.author
                obj = {
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "summary": like.summary,
                    "author":{
                        "type": "author",
                        "id": user["id"],
                        "url": user["url"],
                        "host": user["host"],
                        "displayName": user["diaplayName"],
                        "github": user["github"],
                        "profileImage": user["profileImage"]
                    },
                    "object": like.object
                }
            json_response["data"].append(obj)
        return JsonResponse(json_response)
    else:
        return HttpResponseNotAllowed

