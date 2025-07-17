from django.urls import path
from . import views

app_name = 'webapp'  # 네임스페이스 정의

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),  # 로그인 URL 이름 정의
    path('login/', views.login_view, name='login_view'),


    path('signup/step1/', views.signup_step1, name='signup_step1'),
    path('signup/step2/', views.signup_step2, name='signup_step2'),
    path('signup/step3/', views.signup_step3, name='signup_step3'),

    path('logout/', views.logout_view, name='logout_view'),  # 로그아웃 경로
    path('mypage/', views.mypage_view, name='mypage_view'),  # 마이페이지 경로
    path('after_login/', views.login_view, name='after_login'),  # 로그인 후 페이지 경로

    path('do_tulink1/', views.do_tulink1, name='do_tulink1'),  # Tulink 페이지 1 추가
    path('do_tulink2/', views.do_tulink2, name='do_tulink2'),
    path('do_tulink3/', views.do_tulink3, name='do_tulink3'),

    path('choice_tulink/', views.choice_tulink, name='choice_tulink'),  # 새로운 경로 추가


]
