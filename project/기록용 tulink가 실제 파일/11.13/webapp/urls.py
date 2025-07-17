from django.urls import path
from . import views

app_name = 'webapp'  # 네임스페이스 정의

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),  # 로그인 URL 이름 정의

    path('signup/step1/', views.signup_step1, name='signup_step1'),
    path('signup/step2/', views.signup_step2, name='signup_step2'),
    path('signup/step3/', views.signup_step3, name='signup_step3'),


]
