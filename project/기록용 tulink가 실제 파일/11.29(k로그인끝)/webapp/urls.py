from django.urls import path
from . import views

app_name = 'webapp'

urlpatterns = [
    # 메인 페이지
    path('', views.index, name='index'),  # 메인 페이지 경로

    # 로그인/로그아웃
    path('login/', views.login_view, name='login'),  # 로그인 경로
    path('logout/', views.logout_view, name='logout_view'),  # 로그아웃 경로

    # 회원가입 단계
    path('signup/step1/', views.signup_step1, name='signup_step1'),
    path('signup/step2/', views.signup_step2, name='signup_step2'),
    path('signup/step3/', views.signup_step3, name='signup_step3'),

    # 로그인 후 페이지
    path('after_login/', views.after_login_view, name='after_login'),  # 수정된 경로

    # 마이페이지 및 계정 관리
    path('mypage/', views.mypage_view, name='mypage_view'),  # 마이페이지 경로
    path('delete_account/', views.delete_account_view, name='delete_account'),  # 회원탈퇴

    # Tulink 관련 경로
    path('do_tulink1/', views.do_tulink1, name='do_tulink1'),
    path('do_tulink2/', views.do_tulink2, name='do_tulink2'),
    path('do_tulink3/', views.do_tulink3, name='do_tulink3'),
    path('choice_tulink/', views.choice_tulink, name='choice_tulink'),

    # 튜터링 관련 경로
    path('reserve_tutor/<int:user_id>/', views.reserve_tutor_view, name='reserve_tutor'),
    path('complete/', views.complete_view, name='complete'),
    path('tutoring/submit/<int:user_id>/', views.tutoring_submit, name='tutoring_submit'),

    # 사용자 정보 수정 및 결제
    path('edit_user/', views.edit_user_view, name='edit_user'),
    path('buy_link/', views.buy_link_view, name='buy_link'),

    # QR 스캔 경로
    path('scan_qr/', views.scan_qr_view, name='scan_qr'),
]
