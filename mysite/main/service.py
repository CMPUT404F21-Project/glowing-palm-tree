from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotModified, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
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
        "items": [],
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
        json_response["items"].append(user_object)

    return JsonResponse(json_response)

def retrive_user(response, author_id):
    if response.method == "GET":
        
        user = get_object_or_404(User, localId=author_id)
        
        json_response = {
                "type": "author",
                "id": user.id,
                "url": user.url,
                "host": user.host,
                "displayName": user.username,
                "github":user.github,
                "profileImage": user.profileImage
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
        "items": [],
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
        json_response["items"].append(user_object)
    return JsonResponse(json_response)

def manage_followers(response, author_id, foreign_author_id):
    if response.method == "GET":
        user = get_object_or_404(User, localId=author_id)
        follower = Following.objects.filter(user__exaxt=user.id, following_user__exact=foreign_author_id)
        if follower.exists():
            return JsonResponse({"follower":True})
        else:
            return JsonResponse({"follower":False})

    elif response.method == "PUT":
        pass
    elif response.method == "DELETE":
        pass
    else:
        return HttpResponseNotAllowed()

def manage_posts(response, author_id, post_id):
    if response.method == "GET":
        url = response.build_absolute_uri()
        print(url, "++++++++++++++++++")
        url = url.replace("/service", "")
        url = url.replace("localhost", "127.0.0.1")
        print(url, "__________________")
        ls = get_object_or_404(Moment, id=url)
        user = ls.user
        json_response = {
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
        return JsonResponse(json_response)

    elif response.method == "POST":
        pass
    elif response.method == "DELETE":
        pass
    elif response.methid == "PUT":
        pass
    else:
        return HttpResponseNotAllowed()
    
