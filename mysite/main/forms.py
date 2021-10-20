from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CreateNewMoment(forms.Form):
    content = forms.CharField(label="title", max_length=2000)
    public = forms.BooleanField(required=False)

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]