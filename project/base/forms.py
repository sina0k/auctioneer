from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User, Bid


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'نام'
        self.fields['name'].widget.attrs['class'] = 'form-control custom-class'

        self.fields['username'].label = 'نام کاربری'
        self.fields['username'].help_text = '۱۵۰ کاراکتر یا کمتر، حروف، اعداد و یا @/./+/-/_'
        self.fields['username'].widget.attrs['class'] = 'form-control custom-class'

        self.fields['email'].label = 'ایمیل'
        self.fields['email'].widget.attrs['class'] = 'form-control custom-class'

        self.fields['password1'].label = 'رمز عبور'
        self.fields['password1'].widget.attrs['class'] = 'form-control custom-class'
        self.fields['password1'].help_text = None

        self.fields['password2'].label = 'تکرار رمز عبور'
        self.fields['password2'].widget.attrs['class'] = 'form-control custom-class'
        self.fields['password2'].help_text = None


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email']


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        #DONT FORGET AVATAR IN THE FIELDS
        fields = ['name', 'username', 'email', 'address', 'phone', 'bio']
