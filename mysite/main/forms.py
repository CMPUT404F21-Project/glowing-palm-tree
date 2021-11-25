from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import fields
from .models import User, Moment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
import datetime




class CreateNewMoment(forms.ModelForm):

    
    title = forms.CharField(label="title", max_length=2000, 
                                widget=forms.TextInput({
                                    'class':'form-control',
                                    'placeholder':'Title'
                                }), required=True)
    content = forms.CharField(label="content", max_length=10485760,
                             widget=forms.Textarea({
                                    'class':'form-control',
                                    'placeholder':'Content'
                                }), required=False)
    CHOICES= (
    ('Public','Public'),
    ('Friend','Friend'),
    ('Unlisted','Unlisted')
    )
    CHOICES2= (
    ('plain text','plain text'),
    ('markDown','markDown'),
    ('application','application'),
    ('JPEG', 'JPEG'),
    ('PNG', 'PNG'),
    )
    visibility = forms.ChoiceField(widget=forms.Select, choices=CHOICES)
    contentType = forms.ChoiceField(widget=forms.Select, choices=CHOICES2)
    fileSelect = forms.FileField(label='fileSelect', required=False)

    class Meta:
        model = Moment
        fields = {"title", 'content',  'visibility', 'contentType', 'fileSelect'}
    

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UserProfileEdit(forms.ModelForm):
    
    username = forms.CharField()
    email = forms.EmailField()
    github = forms.CharField()
    class Meta:
        model = User
        fields = ["username", "email", "github"]

