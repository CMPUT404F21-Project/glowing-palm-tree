from django import forms

class CreateNewPostList(forms.Form):
    name = forms.CharField(label="title", max_length=2000)
    public = forms.BooleanField(required=False)