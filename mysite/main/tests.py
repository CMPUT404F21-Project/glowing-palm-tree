from django.test import TestCase, Client

from urllib.parse import urlencode
from .models import *
from .forms import *
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import SimpleUploadedFile

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


class TestFriend(TestCase):

    def setUp(self):
        data = urlencode({"username": "yiyang9", "email":"yiyang9@ulaberta.ca", "password1":"Jackie608", "password2":"Jackie608"})
        response = self.client.post("/register/", data, content_type="application/x-www-form-urlencoded")
        self.client.login(username="yiyang9", password="Jackie608")
        
        self.otherclient = Client()
        data = urlencode({"username": "other1", "email":"other1@ulaberta.ca", "password1":"Testuser1", "password2":"Testuser1"})
        response = self.otherclient.post("/register/", data, content_type="application/x-www-form-urlencoded")
        self.otherclient.login(username="other1", password="Testuser1")
        
    def test_Send_Recieve_Friend_Request(self):
        id1 = User.objects.all()[0].localId
        id2 = User.objects.all()[1].localId
        addr="/friendRequest/"+id1+"/"+id2
        # mock sending friend request
        response = self.client.get(addr)
        
        addr="/friendRequest/"+id2+"/"+id1
        response = self.otherclient.get(addr)
        addr = "/author/"+id2+"/inbox/"
        response = self.otherclient.get(addr)
        self.assertContains(response, 'yiyang9 just followed you!')
        
    def test_Real_Friend(self):
        
        id1 = User.objects.all()[0].localId
        id2 = User.objects.all()[1].localId
        addr="/friendRequest/"+id1+"/"+id2
        
        response = self.client.get(addr)
        self.assertEqual(response.status_code, 302)
        
        addr="/friendRequest/"+id2+"/"+id1
        response = self.otherclient.get(addr)
        self.assertEqual(response.status_code, 302)
        
        response = self.otherclient.get("/getFriend/")
        self.assertContains(response, 'yiyang9')
        response = self.client.get("/getFriend/")
        self.assertContains(response, 'other1')
        
    def test_Unfollow(self):
        id1 = User.objects.all()[0].localId
        id2 = User.objects.all()[1].localId
        addr = "/friendRequest/"+id1+"/"+id2
        # mock sending friend request
        response = self.client.get(addr)
        addr = "/friendRequest/"+id2+"/"+id1
        response = self.otherclient.get(addr)
        
        # mock unfriend
        addr = "/unfollow/"+id2
        response = self.client.get(addr)
        # should not be friend anymore
        response = self.otherclient.get("/getFriend/")
        self.assertNotContains(response, 'yiyang9')


class TestMoment(TestCase):

    def setUp(self):
        data = urlencode({"username": "yiyang9", "email":"yiyang9@ulaberta.ca", "password1":"Jackie608", "password2":"Jackie608"})
        response = self.client.post("/register/", data, content_type="application/x-www-form-urlencoded")
        self.client.login(username="yiyang9", password="Jackie608")
        
        self.otherclient = Client()
        data = urlencode({"username": "other1", "email":"other1@ulaberta.ca", "password1":"Testuser1", "password2":"Testuser1"})
        response = self.otherclient.post("/register/", data, content_type="application/x-www-form-urlencoded")
        self.otherclient.login(username="other1", password="Testuser1")


    @csrf_exempt
    def test_New_Public_Post(self):
        data = urlencode({ "title":"test", "content":"thisistestcontent", "visibility":"Public", "contentType":"text/plain"})
        id = User.objects.all()[0].localId
        addr = "/author/"+id+"/posts/"
        # mock user new post acticity
        response = self.client.post(addr, data, content_type="application/x-www-form-urlencoded")
        
        # check other can see it on main page
        response = self.otherclient.get("/home/")
        self.assertContains(response, 'thisistestcontent')

        

    @csrf_exempt
    def test_Edit_Public_Post(self):
        data = urlencode({ "title":"test", "content":"thisistestcontent", "visibility":"Public", "contentType":"text/plain"})
        id = User.objects.all()[0].localId
        addr = "/author/"+id+"/posts/"
        # mock user new post acticity
        response = self.client.post(addr, data, content_type="application/x-www-form-urlencoded")
        
        postid = Moment.objects.all()[0].localId
                
        #addr = "/momentEdit/" + postid
        addr = "/author/"+id+"/posts/"+postid
        data = urlencode({"title":"change", "content":"contentshouldchange", "visibility":"Public", "contentType":"text/plain"})

        # mock edit post activity
        response = self.client.post(addr, data, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get("/home/")
        self.assertContains(response, 'contentshouldchange')
        
    def test_Delete_Post(self):
        data = urlencode({ "title":"test", "content":"thisistestcontent", "visibility":"Public", "contentType":"text/plain"})
        id = User.objects.all()[0].localId
        addr = "/author/"+id+"/posts/"
        # mock user new post acticity
        response = self.client.post(addr, data, content_type="application/x-www-form-urlencoded")
        
        response = self.client.get("/home/")
        self.assertContains(response, 'thisistestcontent')
        
        postid = Moment.objects.all()[0].localId
                
        addr = "/author/"+id+"/posts/" +postid
        data = urlencode({"_METHOD":"Delete"})

        response = self.client.post(addr, data, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200)
        
        # nothing should be there
        response = self.client.get("/home/")
        self.assertNotContains(response, 'thisistestcontent')
        
    def test_Friend_Post(self):
        data = urlencode({ "title":"test", "content":"thisistestcontent", "visibility":"Friend", "contentType":"text/plain"})
        id = User.objects.all()[0].localId
        addr = "/author/"+id+"/posts/"
        # mock user new post acticity but post is Friend
        response = self.client.post(addr, data, content_type="application/x-www-form-urlencoded")
        
        # i can see my friend post, but other user not friend cannot
        response = self.client.get("/view/")
        self.assertContains(response, 'thisistestcontent')
        
        response = self.otherclient.get("/view/")
        self.assertNotContains(response, 'thisistestcontent')
        response = self.otherclient.get("/home/")
        self.assertNotContains(response, 'thisistestcontent')
        
        # after become real friend, can see in post list
        id1 = User.objects.all()[0].localId
        id2 = User.objects.all()[1].localId
        addr = "/friendRequest/"+id1+"/"+id2
        response = self.client.get(addr)
        
        addr = "/friendRequest/"+id2+"/"+id1
        response = self.otherclient.get(addr)
        
        response = self.otherclient.get("/view/")
        self.assertContains(response, 'thisistestcontent')

        
        
    def test_Unlisted_Post(self):
        data = urlencode({ "title":"test", "content":"thisistestcontent","visibility":"Unlisted", "contentType":"text/plain"})
        id = User.objects.all()[0].localId
        addr = "/author/"+id+"/posts/"
        # mock user new post acticity but post is unlisted
        response = self.client.post(addr, data, content_type="application/x-www-form-urlencoded")
        
        # i can see my unlisted post, but other user not friend cannot
        response = self.client.get("/view/")
        self.assertContains(response, 'thisistestcontent')
        
        response = self.otherclient.get("/view/")
        self.assertNotContains(response, 'thisistestcontent')
        response = self.otherclient.get("/home/")
        self.assertNotContains(response, 'thisistestcontent')
        
    def test_Image_Post(self):
        response = self.client.get("/home/")
        self.assertNotContains(response, 'addImage(contentBody);')
        
        img = SimpleUploadedFile("testimage.jpg", b"file_content", content_type="image/jpeg")
        print(img)
        data = urlencode({ "title":"testimage","visibility":"Public", "contentType":"image/jpeg;base64","fileSelect":img})
        id = User.objects.all()[0].localId
        addr = "/author/"+id+"/posts/"
        # mock user new post acticity but post in image
        response = self.client.post(addr, data, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get("/home/")
        self.assertContains(response, 'addImage(contentBody);')


        
class TestCommentLike(TestCase):

    def setUp(self):
        data = urlencode({"username": "yiyang9", "email":"yiyang9@ulaberta.ca", "password1":"Jackie608", "password2":"Jackie608"})
        response = self.client.post("/register/", data, content_type="application/x-www-form-urlencoded")
        self.client.login(username="yiyang9", password="Jackie608")
        
        self.otherclient1 = Client()
        data = urlencode({"username": "other1", "email":"other1@ulaberta.ca", "password1":"Testuser1", "password2":"Testuser1"})
        response = self.otherclient1.post("/register/", data, content_type="application/x-www-form-urlencoded")
        self.otherclient1.login(username="other1", password="Testuser1")
        
        self.otherclient2 = Client()
        data = urlencode({"username": "other2", "email":"other2@ulaberta.ca", "password1":"Testuser2", "password2":"Testuser2"})
        response = self.otherclient2.post("/register/", data, content_type="application/x-www-form-urlencoded")
        self.otherclient2.login(username="other2", password="Testuser2")
        
    def test_Comment_to_other(self):
        data = urlencode({ "title":"test", "content":"thisistestcontent", "visibility":"Public", "contentType":"text/plain"})
        id = User.objects.all()[0].localId
        addr = "/author/"+id+"/posts/"
        # mock user new post acticity
        response = self.client.post(addr, data, content_type="application/x-www-form-urlencoded")
    
        id = User.objects.all()[0].localId
        postid = Moment.objects.all()[0].localId
        addr = "/author/"+id+"/posts/"+postid
        data = urlencode({"url":addr,"content":"Atestcomment"})
        addr2 = addr+"/comments"
        response = self.otherclient1.post(addr2, data, content_type="application/x-www-form-urlencoded")
        
        response = self.otherclient1.get(addr)
        self.assertContains(response, 'Atestcomment')
        
    def test_Friend_Post_Comment(self):
        data = urlencode({ "title":"test", "content":"thisistestcontent", "visibility":"Friend", "contentType":"text/plain"})
        id = User.objects.all()[0].localId
        addr = "/author/"+id+"/posts/"
        # mock user new post acticity
        response = self.client.post(addr, data, content_type="application/x-www-form-urlencoded")
        
        id1 = User.objects.all()[1].localId
        addr = "/friendRequest/"+id+"/"+id1
        # mock sending friend request
        response = self.client.get(addr)
        addr = "/friendRequest/"+id1+"/"+id
        response = self.otherclient1.get(addr)
        
        id2 = User.objects.all()[2].localId
        addr = "/friendRequest/"+id2+"/"+id
        # mock sending friend request
        response = self.client.get(addr)
        addr = "/friendRequest/"+id+"/"+id2
        response = self.otherclient2.get(addr)

    
        postid = Moment.objects.all()[0].localId
        addr = "/author/"+id+"/posts/"+postid
        data = urlencode({"url":addr,"content":"Atestcomment"})
        addr2 = addr+"/comments"
        response = self.otherclient1.post(addr2, data, content_type="application/x-www-form-urlencoded")
        
        # author and comment owner can see, other friends who can access post can't see
        response = self.client.get(addr)
        self.assertContains(response, 'Atestcomment')
        response = self.otherclient1.get(addr)
        self.assertContains(response, 'Atestcomment')
        
        response = self.otherclient2.get(addr)
        self.assertNotContains(response, 'Atestcomment')
        
        
    def test_Like(self):
        data = urlencode({ "title":"test", "content":"thisistestcontent", "visibility":"Public", "contentType":"text/plain"})
        id = User.objects.all()[0].localId
        addr = "/author/"+id+"/posts/"
        # mock user new post acticity
        response = self.client.post(addr, data, content_type="application/x-www-form-urlencoded")
    
        postid = Moment.objects.all()[0].localId
        
        addr = "/author/"+id+"/inbox/"
        addr2 = "http://testserver/author/"+id+"/posts/"+postid
        self.assertEqual(Moment.objects.all()[0].id,addr2)
        
        # mock other like post
        data = urlencode({"url":addr2,"type":"like",'likeButton': addr2})
        response = self.otherclient1.post(addr, data, content_type="application/x-www-form-urlencoded")
        
        response = self.client.get(addr)
        self.assertContains(response, 'like')

class TestProfile(TestCase):
    def setUp(self):
        data = urlencode({"username": "yiyang9", "email":"yiyang9@ulaberta.ca", "password1":"Jackie608", "password2":"Jackie608"})
        response = self.client.post("/register/", data, content_type="application/x-www-form-urlencoded")
        self.client.login(username="yiyang9", password="Jackie608")
        
    def test_Edit_profile(self):
        data = urlencode({ "username":"yiyang9", "email":"yiyang9@ulaberta.ca","github":"https://github.com/CMPUT404F21-Project/glowing-palm-tree"})
        # mock user edit profile
        response = self.client.post("/userCenterEdit/", data, content_type="application/x-www-form-urlencoded")

        id = User.objects.all()[0].localId
        addr = "/author/"+id
        response = self.client.get(addr)
        self.assertContains(response, 'https://github.com/CMPUT404F21-Project/glowing-palm-tree')
        

       
