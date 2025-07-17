#회원가입에서 추가하기버튼을 위한 forms.py

from django import forms

class TutoringMajorForm(forms.Form):
    tutoring_major = forms.CharField(max_length=100, label="Tutoring Major")
    tutoring_sub_major = forms.CharField(max_length=100, required=False, label="Tutoring Sub-Major")




