from django import forms

class UsernameForm(forms.Form):
    username = forms.CharField(label="username", max_length=16)
    