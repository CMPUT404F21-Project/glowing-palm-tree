from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import fields
from .models import User, Moment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

class CreateNewMoment(forms.Form):

    
    title = forms.CharField(label="title", max_length=2000, 
                                widget=forms.TextInput({
                                    'class':'form-control',
                                    'placeholder':'Title'
                                }), required=True)
    content = forms.CharField(label="content", max_length=2000,
                             widget=forms.Textarea({
                                    'class':'form-control',
                                    'placeholder':'Content'
                                }), required=True)
    markDown = forms.BooleanField(required=False)
    CHOICES= (
    ('1','Public'),
    ('2','Private'),
    )
    visibility = forms.ChoiceField(widget=forms.Select, choices=CHOICES)
    
    class Meta:
        model = Moment
        fields = {"title", 'content', 'markdown', 'visibility'}

    

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
