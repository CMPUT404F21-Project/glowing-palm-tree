from django.core.exceptions import RequestAborted
from django.db.models import base

from django.http.response import Http404, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseNotModified, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from django.http import HttpResponse, HttpResponseRedirect, request
from .models import Inbox, Moment, Comment, Following, Likes, Liked, User, Pending
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
import markdown
# Create your views here.
import mimetypes, urllib3

def is_url_image(url):    
    mimetype,encoding = mimetypes.guess_type(url)
    return (mimetype and mimetype.startswith('image'))

def check_url(url):
    """Returns True if the url returns a response code between 200-300,
       otherwise return False.
    """
    try:
        headers = {
            "Range": "bytes=0-10",
            "User-Agent": "MyTestAgent",
            "Accept": "*/*"
        }

        req = urllib3.Request(url, headers=headers)
        response = urllib3.urlopen(req)
        return response.code in range(200, 209)
    except Exception:
        return False

def is_image_and_ready(url):
    return is_url_image(url) and check_url(url)


def redirectToHome(request):
    return HttpResponseRedirect("/home")


def remotePostDetail(request):
    data = json.loads(request.POST.get("data"))
    remoteUser = data['author']
    content = data['content']
    contentType = data['contentType']
    source = data['source']
    id = data['id']
    print(content)
    print("+++++++++++++")
    if(contentType == "text/markdown"):
        #content = markdown.markdown(content).replace("\r", "<br>")
        content = markdown.markdown(content).replace("\n", "<br>").replace("\"", "")
    return render(request, "main/listRemote.html", {'title':data['title'],"author":remoteUser, "content":content, "contentType": contentType, "source":source, "id":id}) 

def remoteUserDetail(request):
    remoteUser = json.loads(request.POST.get("data"))
    if (remoteUser['host'] == "https://cmput404-socialdistributio-t18.herokuapp.com"):
        team = 18
    elif (remoteUser['host'] == "https://social-distribution-t10.herokuapp.com/api/"):
        team = 10
    elif (remoteUser['host'] == "https://glowing-palm-tree1.herokuapp.com/home"): 
        team = 12
    elif (remoteUser['host'] == "https://cmput404f21t17.herokuapp.com/"): 
        team = 17
    else:
        team = 0
    username = remoteUser['displayName']

    host = remoteUser['host']
    url = remoteUser['url']
    idOnly = url.replace(host+'/author/', '')

    email = "None"
    github = remoteUser['github']

    try:
        profileImage = remoteUser["profileimage"]
    except:
        profileImage = None
    return render(request, "main/otherRemoteUser.html", {"team": team, 'idOnly': idOnly, 'id': remoteUser['id'], 'url': remoteUser['url'], 'host': remoteUser['host'], 'github': github, "email": email, "username": username, 'profileImage': profileImage})

def githubFlow(request, authorId):
    user = get_object_or_404(User, localId=authorId)
    github = user.github
    if(github):
        
        name = github.replace("https://github.com/",'')
        
    else:
        name = None    
    
    return render(request, "main/githubFlow.html", {'name': name})


def commentToPost(response, authorId, postId, commentId):
    comment = Comment.objects.filter(localId=commentId)
    if(comment.exists()):
        comment = comment[0]
    else:
        return HttpResponseNotFound()
    ls = Moment.objects.get(id=comment.moment.id)

    
    if response.method == "GET":
        like = Likes.objects.filter(userId__exact=response.user.id, object__exact=ls.id)
        content = ls.content
        if(ls.contentType == "text/markdown"):
                #content = markdown.markdown(content).replace("\r", "<br>")
                content = markdown.markdown(content).replace("\n", "<br>")
    comments = Comment.objects.filter(moment=ls)
    likeDict = {}
    
    for item in comments:
        if( (Likes.objects.filter(object=item.commentId, userId=response.user.id) ).exists()  ):
            likeDict[item.localId] = True
        else:
            likeDict[item.localId] = False

    likeDict = json.dumps(likeDict)        
    return render(response, "main/list.html", {"ls":ls, 'liked':(like.exists()), 'content':content, "likeDict":likeDict})
    
def flat(arg):
    return arg[0]

def addProfileImage(request, userId):
    if(request.method == "GET"):
        return render(request, "main/editProfileImage.html")
    if(request.method == "POST"):
        url = request.POST.get("img", None)
        user = User.objects.get(id=request.user.id)
        if(url):
            #if(is_image_and_ready(url)):
            user.profileImage = url
            user.save()
        return HttpResponseRedirect("/author/" + userId)


def date_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

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
                p.localId = postId
                p.type = 'post'
                p.source = p.id
                p.origin = p.id
                p.count = 0
                # p.comment = ""
                categories = response.POST.getlist("Categories")
                #p.categories = json.dumps(categories)
                p.categories = categories
                p.user = response.user
                p.published = datetime.datetime.now()
                p.save()
                response.user.moment.add(p)
                
                
                if p.visibility in ["Public", "Friend"]:
                    friend_list = get_friends(response.user)
                    inboxes = Inbox.objects.filter(author__in=friend_list)
                    dict_object = model_to_dict(p)
                    dict_object['user'] = response.user.displayName
                    dict_object['userLink'] = response.user.id
                    if(p.contentType == "text/markdown"):
                        dict_object["content"] =   markdown.markdown(dict_object["content"]).replace("\n", "<br>").replace("\"","").replace("\\","")
                    send_to_inbox(dict_object, list(inboxes))

                    
                # p = serializers.serialize('json', [p,])
                # p = json.loads(p)[0]
                # p = json.dumps(p)
                content = p.content
                contentType = p.contentType
                if(contentType == "text/markdown"):
                    #content = markdown.markdown(content).replace("\r", "<br>")
                    content = markdown.markdown(content).replace("\n", "<br>").replace("\"", "")
                   
                likeDict = json.dumps({}) 
                return render(response, "main/list.html", {"ls":p, "content":content, "contentType": contentType, "likeDict": likeDict})
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
        content = showListFull.values_list('id','content')
        
        content = [x[1] for x in content ]

        page =  int(response.GET.get("page", 1))
        size =  int(response.GET.get("size", 5))
        
        
        # btType = response.GET.get("type", '')

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
        
        for i in range(len(showList)):
            if showList[i].contentType == 'text/markdown':
                print(type(showContent[i]))
                showContent[i] = markdown.markdown(showContent[i]).replace("\n", "<br>").replace("\"","").replace("\\","")

        maxPage = math.ceil(len(lsList)/size)
        showContent = json.dumps(showContent)

        return render(response, "main/aPostList.html", {"authorId":authorId,"showList":showList, "size":size, "page": page, "maxPage":maxPage, "content":showContent})
        

def userMoment(response, authorId, postId):
    #url = "http://localhost:8000/" + "author/" + authorId + "/posts/" + postId
    url = urlparse(response.build_absolute_uri())
    cleanUrl = response.build_absolute_uri().replace("?" + url.query,'')
    print(cleanUrl)

    ls = Moment.objects.filter(id__exact=cleanUrl )
    if(ls.exists()):
        ls = ls[0]
    else:
        print(url)
        return HttpResponseNotFound()
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
        if(ls.contentType == "text/markdown"):
                #content = markdown.markdown(content).replace("\r", "<br>")
                content = markdown.markdown(content).replace("\n", "<br>")

        comments = Comment.objects.filter(moment=ls)
        likeDict = {}
        
        for item in comments:
            if( (Likes.objects.filter(object=item.commentId, userId=response.user.id) ).exists()  ):
                likeDict[item.localId] = True
            else:
                likeDict[item.localId] = False

        likeDict = json.dumps(likeDict) 
        return render(response, "main/list.html", {"ls":ls, 'liked':(like.exists()), 'content':content, "likeDict":likeDict })
        
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
                like = Likes.objects.filter(userId__exact=response.user.id, object__exact=ls.id)
                content = ls.content
                if(ls.contentType == "text/markdown"):
                        #content = markdown.markdown(content).replace("\r", "<br>")
                        content = markdown.markdown(content).replace("\n", "<br>")

                comments = Comment.objects.filter(moment=ls)
                likeDict = {}
                
                for item in comments:
                    if( (Likes.objects.filter(object=item.commentId, userId=response.user.id) ).exists()  ):
                        likeDict[item.localId] = True
                    else:
                        likeDict[item.localId] = False

                likeDict = json.dumps(likeDict) 
                return render(response, "main/list.html", {"ls":ls, 'liked':(like.exists()), 'content':content, "likeDict":likeDict })

    elif response.method == "DELETE":
        ls.delete()
        return HttpResponseRedirect("/author/%s/posts/%s" %(authorId, postId))

    return render(response, "main/list.html", {"ls":ls})

def home(response):
    if(response.user.is_anonymous):
        pass
    elif(not response.user.pending.exists()):
        response.user.authorized = True
        response.user.save()
    else:
        pass
    moments = Moment.objects.filter(visibility__iexact="Public")
    moments = moments.order_by("-published")
    content = list(moments.values_list('content', flat=True))
    contentType = list(moments.values_list('contentType', flat=True))
    for i in range(len(contentType)):
        if contentType[i] == 'text/markdown':
            content[i] = markdown.markdown(content[i]).replace("\n", "<br>").replace("\"","").replace("\\","")
    
    content = json.dumps({"content":content})
    form = CreateNewMoment()

    return render(response, "main/home.html", {"form":form, "moments":moments, "content":content})


def view(response):

    categoriesNeeded = response.POST.getlist("Categories")

    teams = response.POST.getlist("Teams")

    print(teams)

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

    

    content1 = showList.values_list('id','content','contentType','categories')
        
    content = [x[1] for x in content1 ]
    contentType =  [x[2] for x in content1 ]
    categories =  [x[3] for x in content1 ]
    showList = list(showList)
    for i in range(len(contentType)):
        if contentType[i] == 'text/markdown':
            content[i] = markdown.markdown(content[i]).replace("\n", "<br>").replace("\"","").replace("\\","")
            #for JSON.parse to run I have to do this
    

    if(len(categoriesNeeded) == 0):
        content = json.dumps(content)    
    else:
        showListFiltered = []
        contentFiltered = []
        for i in range(len(showList)):
            included = True
            for category in categoriesNeeded:
                if category not in categories[i]:
                    
                    included = False
            if included:
                contentFiltered.append(content[i])
                showListFiltered.append(showList[i])
        content = json.dumps(contentFiltered)   
        showList = showListFiltered 

    team12 = False
    team18 = False
    team10 = False
    team02 = False
    team03 = False

    if "Team12" in teams:
        team12 = True
    if "Team18" in teams:
        team18 = True
    if "Team10" in teams:
        team10 = True
    if "Team02" in teams:
        team02 = True
    if "Team03" in teams:
        team03 = True


    return render(response, "main/view.html", {"showList":showList, 'user':response.user, 'content':content, 
                                                "categoriesNeeded": json.dumps(categoriesNeeded),
                                                "team12": team12, "team10": team10, "team18":team18, "team02":team02, "team03":team03})

def browseAuthors(response):
    localAuthors = User.objects.exclude(displayName=None).filter(is_superuser=False)
    localAuthors = localAuthors.order_by('displayName')
    return render(response, "main/browseAuthor.html", {"localAuthors":localAuthors})


def userCenter(response, id):
    if(response.user.localId == id):
        showList = Moment.objects.filter(user__exact=response.user).order_by("-published")
        content = list(showList.values_list('content', flat=True))
        contentType = list(showList.values_list('contentType', flat=True))
        for i in range(len(contentType)):
            if contentType[i] == 'text/markdown':
                content[i] = markdown.markdown(content[i]).replace("\n", "<br>").replace("\"","").replace("\\","")
        profileImage = False

        if response.user.profileImage != None:
            profileImage = True
      
        content = json.dumps(content)
        return render(response, "main/userCenter.html", {"user":response.user,"showList":showList, "content":content, "profileImage": profileImage},)
    else:
        otherUser = User.objects.get(localId=id)
        user = response.user
        followList = Following.objects.filter(user__exact=user, following_user__exact=otherUser)
        following = followList.exists()

        profileImage = False
        if otherUser.profileImage != None:
            profileImage = True
     
        return render(response, "main/otherUser.html", {"otherUser":otherUser, "following":following, "profileImage":profileImage})

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
            createdUser.type = "author"
            createdUser.displayName = createdUser.username
            createdUser.host = host
            createdUser.id = userId
            createdUser.url = userId
            createdUser.localId = localId
            createdUser.save()

            initial_list = json.dumps([])
            
            inbox = Inbox.objects.create(author=createdUser, type="inbox",items = initial_list)
            inbox.save()
            pending = Pending.objects.create(pendingUser=createdUser)
            pending.save()
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

        inbox = Inbox.objects.get(author=otherUser)
        item = {"user":response.user.displayName, "userId":response.user.id, "type":"follow"}
        send_to_inbox(item, [inbox])

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
        obj_type = response.POST.get("type", "")
        url = response.POST.get("url", "")
        


        if(obj_type == "commentLike"):
            localId = response.POST.get("id", "")
            comment = Comment.objects.get(localId=localId)
            inbox = Inbox.objects.get(author=comment.author)

            user = comment.author
            author = {
                "type": "author",
                "id": user.id,
                "url": user.url,
                "host": user.host,
                "displayName": user.displayName,
                "github": user.github,
                "profileImage": user.profileImage
            }
            author = json.dumps(author)
            summary = "%s likes your comment under post: %s"%(response.user.displayName, comment.moment.title)
            like = Likes.objects.create(object=comment.commentId, type="like", author=author, summary=summary, userId=response.user.id)
            dict_object = model_to_dict(like)
            #print(dict_object)
            items = inbox.items
            items = json.loads(items)
            items.append(dict_object)
            items = json.dumps(items)
            inbox.items = items
            inbox.save()
            return HttpResponseRedirect(url)


            
        moment = Moment.objects.get(id=url)
        selfName = response.user.displayName
        
        
        if(obj_type == "like"):
            print("hahahahaha")
            inbox = Inbox.objects.get(author=moment.user)
            user = moment.user
            author = {
                "type": "author",
                "id": user.id,
                "url": user.url,
                "host": user.host,
                "displayName": user.displayName,
                "github": user.github,
                "profileImage": user.profileImage
            }
            author = json.dumps(author)
            summary = "%s likes your Post(title: %s)"%(selfName, moment.title)
            like = Likes.objects.create(object=url, type="like", author=author, summary=summary, userId=response.user.id)
            moment.count = moment.count + 1
            moment.save()
            dict_object = model_to_dict(like)
            #print(dict_object)
            items = inbox.items
            items = json.loads(items)
            items.append(dict_object)
            items = json.dumps(items)
            inbox.items = items
            inbox.save()
            return HttpResponseRedirect(url)
        elif obj_type == 'share':
            users = response.POST.getlist("userSelect")
            user = response.user

            inboxes = Inbox.objects.filter(author__in=users)
            dict_object = model_to_dict(moment)
            if(moment.contentType == "text/markdown"):
                dict_object["content"] =   markdown.markdown(dict_object["content"]).replace("\n", "<br>").replace("\"","").replace("\\","")
            print(moment.contentType)

                
            
            dict_object['user'] = selfName
            dict_object['userLink'] = user.id

            dict_object["author"] = {
                "type": "author",
                "id": user.id,
                "url": user.url,
                "host": user.host,
                "displayName": user.displayName,
                "github": user.github,
                "profileImage": user.profileImage
            }

            send_to_inbox(dict_object, list(inboxes))

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
    comment.localId = commentUuid
    comment.moment = moment
    
    print("outside")
    if response.method == "POST":
        print("enter")
        comment.content = response.POST.get("content")
        comment.author = response.user
        comment.type = "comment"
        comment.published = str(datetime.datetime.now())
        comment.save()
    url = response.POST.get("url")
    return HttpResponseRedirect(url)

def momentRepost(response, authorId, postId):
    url = response.build_absolute_uri().replace("/share", "")
    ls = Moment.objects.filter(id__exact=url)
    user = User.objects.filter(localId__exact=authorId)
    ls = ls[0]
    user = user[0]
    uuid = str(uuid4())
    newId = response.user.id + "/posts/" + uuid
    #print(user)
    #print(ls)
    newLs = Moment.objects.create(id=newId, localId=uuid, content=ls.content, type="post", contentType=ls.contentType, user=response.user, origin = ls.origin,
                                    source=ls.id, count=0, published=str(datetime.datetime.now()), title=ls.title,visibility=ls.visibility, categories=ls.categories )

    # newLs.content = ls.content
    # newLs.contenType = ls.contentType
    # newLs.user = response.user
    # newLs.source = user.id
    # newLs.published = datetime.datetime.now()
    newLs.save()
    content = ls.content
    contentType = ls.contentType
    if(contentType == "text/markdown"):
        #content = markdown.markdown(content).replace("\r", "<br>")
        content = markdown.markdown(content).replace("\n", "<br>").replace("\"", "")
    likeDict = json.dumps({})  
    return render(response, "main/list.html", {"ls":newLs, "content":content, "contentType": contentType, "likeDict": likeDict}) 


def getFriend(response):

    followerList = Following.objects.filter(following_user__exact=response.user).values_list('user',flat=True)
    followingList = Following.objects.filter(user__exact=response.user).values_list('following_user',flat=True)
    friendList = list(followerList.intersection(followingList))

    friendList = User.objects.filter(id__in=friendList)
    

    friendListName = list(friendList.values_list("displayName",flat=True))
    friendListId = list(friendList.values_list("id", flat=True))

    nameListJs = json.dumps(friendListName)
    idListJs = json.dumps(friendListId)

    return JsonResponse({"nameList":nameListJs, "idList":idListJs})

def remoteAuthorPosts(response, team, authorId):
    return render(response, "main/aPostListRemote.html", {"id": authorId, "team":team})

# def getForm(response, formType):
#     if formType == "file":
#         form = CreateNewImageMoment()
#     else:
#         form = CreateNewMoment()
#     renderHtml = render_to_string("main/home.html", {"form": form})
#     print(renderHtml)
#     return JsonResponse({"form":renderHtml})
    
