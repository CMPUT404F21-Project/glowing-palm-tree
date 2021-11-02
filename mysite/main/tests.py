from django.test import TestCase, Client

from urllib.parse import urlencode
from .models import *
from django.urls import reverse

# Create your tests here.

class TestUser(TestCase):

    def test_signUp(self):
        data = urlencode({"username": "yiyang9", "email":"yiyang9@ulaberta.ca", "password1":"Jackie608", "password2":"Jackie608"})
        response = self.client.post("/register/", data, content_type="application/x-www-form-urlencoded")


    def test_login(self):
        # Sign-up 
        data = urlencode({"username": "yiyang9", "email":"yiyang9@ulaberta.ca", "password1":"Jackie608", "password2":"Jackie608"})
        response = self.client.post("/register/", data, content_type="application/x-www-form-urlencoded")

        data = urlencode({"username": "yiyang9", "password":"Jackie608"})
        response = self.client.post("/login/", data, content_type="application/x-www-form-urlencoded")
        # print(response.content)
        # self.client.login(username="yiyang9", password="Jackie608")
        
        response = self.client.get('/home/')
        self.assertContains(response, 'yiyang9')


class TestMoment(TestCase):

    def test_New_Post(self):
        # Sign-up 
        data = urlencode({"username": "yiyang9", "email":"yiyang9@ulaberta.ca", "password1":"Jackie608", "password2":"Jackie608"})
        response = self.client.post("/register/", data, content_type="application/x-www-form-urlencoded")
        # Login 
        data = urlencode({"username": "yiyang9", "password":"Jackie608"})
        response = self.client.post("/login/", data, content_type="application/x-www-form-urlencoded")
        #self.client.login(username="yiyang9", password="Jackie608")

        #data = urlencode({"_METHOD":"PUT", "title":"test", "content":"thisistestcontent", "visibility":"Public"})
        #response = self.client.post("/home/", data, content_type="application/x-www-form-urlencoded")
        #print(response)

        #tester = User()
        # for u in User.objects.all():
        #     tester = u
        tester = User.objects.all()[0]

        post = Moment(title="test", content="test content", visibility = "Public", user = tester)
        post.save()
        post.refresh_from_db()

        response = self.client.get('/home/')
        #print(response.content)
        self.assertContains(response, 'test content')