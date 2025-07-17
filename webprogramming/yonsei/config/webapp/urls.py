#파일 자체를 추가함 url

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views #8장

app_name = 'webapp'  # 애플리케이션 이름을 지정하여 URL을 네임스페이스로 구분

urlpatterns = [
    path('', views.index, name='index'),  # 웹앱의 메인 페이지 URL 패턴
    path('webapp/service/', views.service, name='service'),  # 웹앱의 'service' 페이지 URL 패턴
    path('webapp/grid/<int:type>', views.grid, name='grid'),  #  #3장템플릿 시스템
    path('webapp/bible/',views.bible,name='bible'),#4장 DB
    path('webapp/post',views.post,name='post'),  #5장 DB게시판 읽기
    path('webapp/board',views.board,name='board'),#5장 DB게시판 읽기

    path('webapp/rhema/write/<int:id>', views.rhema_write, name='rhema_write'),#6장 게시판 수정삭제
    path('webapp/rhema/read/<int:id>', views.rhema_read, name='rhema_read'),#6장 게시판 수정삭제
    path('webapp/rhema/update/<int:id>', views.rhema_update, name='rhema_update'),#6장 게시판 수정삭제
    path('webapp/rhema/delete/<int:id>', views.rhema_delete, name='rhema_delete'),#6장 게시판 수정삭제


    #8장
    path('webapp/logout/', auth_views.LogoutView.as_view(), name='logout'),


    path('webapp/login/',
         auth_views.LoginView.as_view(template_name='webapp/login.html'),
         name='login'),

    path('webapp/logout/',
         auth_views.LogoutView.as_view(),
         name='logout'),

    path('webapp/signup/',
         views.signup,
         name='signup'),

]

