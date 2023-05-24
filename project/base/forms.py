from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User


USER_CREATION_FIELDS = ['name', 'username', 'email', 'password1', 'password2']
USER_UPDATE_FIELDS = ['name', 'username', 'email', 'address', 'phone', 'bio', 'avatar']

FIELD_LABELS = {
    'name': 'نام',
    'username': 'نام کاربری',
    'email': 'ایمیل',
    'password1': 'رمز عبور',
    'password2': 'تکرار رمز عبور',
    'address': 'آدرس',
    'phone': 'تلفن',
    'bio': 'بیو',
    'avatar': 'آواتار'
}

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = USER_CREATION_FIELDS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].help_text = 'حروف، اعداد و یا @/./+/-/_'
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

        for field in USER_CREATION_FIELDS:
            self.fields[field].label = FIELD_LABELS[field]
            self.fields[field].widget.attrs['class'] = 'form-control custom-class'


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email']


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        #DONT FORGET AVATAR IN THE FIELDS
        fields = USER_UPDATE_FIELDS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].help_text = 'حروف، اعداد و یا @/./+/-/_'

        for field in USER_UPDATE_FIELDS:
            self.fields[field].label = FIELD_LABELS[field]
            self.fields[field].widget.attrs['class'] = 'form-control custom-class'
