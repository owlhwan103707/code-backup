#5장 DB게시판 읽기
from django import forms

from .models import Board
from .models import Rhema #6장 DB게시판 수정

from django.contrib.auth.forms import UserChangeForm #8장
from django.contrib.auth.models import User #8장

from django.contrib.auth.forms import UserCreationForm #8장수정 핵심!!!


class PostForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ('subject','artical',)

#6장 DB게시판 수정
class WriteForm(forms.ModelForm):
    class Meta:
        model = Rhema
        fields = ('rhema',)

        widgets = { 'rhema':forms.Textarea(attrs={'class':'form-control','rows':20,'cols':70,}),}
        labels ={'rhema':'',}     #존나레전드 에러 잘 고치시길

#8장
class UserForm(UserCreationForm):
    email=forms.EmailField(label="이메일")

    class Meta:
        model=User
        fields=("username","email")

