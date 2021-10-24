from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Moment, Comment
from .forms import CreateNewMoment
from .forms import RegisterForm
from django.views.decorators.csrf import csrf_protect
# Create your views here.

def index(response, id):
    ls = Moment.objects.get(id=id)
    if ls in response.user.moment.all():
        if response.method == "POST" :
            # print(response.POST)
            if response.POST.get("save"):
                for comment in ls.comment_set.all():
                    if response.POST.get("c"+ str(comment.id)) == "clicked":
                        comment.complete = True
                    else:
                        comment.complete = False
                    comment.save()
            elif response.POST.get("newPost"):
                txt = response.POST.get("new")
                if len(txt) > 2:
                    ls.comment_set.create(content=txt, complete=False)
                else:
                    print("invalid")

        return render(response, "main/list.html", {"ls":ls})
    return render(response, "main/view.html", {})

def home(response):
    if response.method == "POST":
        form = CreateNewMoment(response.POST)
        if form.is_valid():
            n = form.cleaned_data["content"]
            p = form.cleaned_data["public"]
            
    return render(response, "main/home.html", {})

def create(response):
    if response.method == "POST":
        form = CreateNewMoment(response.POST)
        if form.is_valid():
            n = form.cleaned_data["content"]
            p = Moment(content=n)
            p.save()
            response.user.moment.add(p)
            return HttpResponseRedirect("/%i" %p.id)
        else:
            print(form.errors)
    else:
        form = CreateNewMoment()
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
