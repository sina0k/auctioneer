from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User, Bid


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email']


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        #DONT FORGET AVATAR IN THE FIELDS
        fields = ['name', 'username', 'email', 'address', 'phone', 'bio']
