"""
Admin 사이트에서 Django 모델을 관리하기 위한 설정 파일입니다.
이 코드는 주로 `admin.py`에서 사용되며, Django Admin 페이지에서 데이터 관리 기능을 제공합니다.
모델의 필드들에 대해 필터링, 검색, 출력 설정 등을 정의하여 관리자 인터페이스를 구성합니다.
주로 관리자는 admin 사이트를 통해 데이터의 정확성을 검토하고 관리할 수 있습니다.

연관된 파일:
- `models.py`: 이 파일의 모델들을 Admin에 등록하여 관리합니다.
- Admin 페이지: Django가 제공하는 기본 Admin 인터페이스에서 활용됩니다.
"""

from django.contrib import admin
from .models import User, UserTulink, TutoringRequest, Payment, Feedback, Major, Link,DoTulink  # 모델들 임포트

# User 모델을 Admin에 등록
@admin.register(User)  # User 모델 등록
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'my_current_major', 'my_tutoring_major', 'my_available_days')
    # Admin 페이지에서 표시할 필드 목록
    search_fields = ('name', 'email', 'my_current_major')
    # Admin 페이지에서 검색 가능 필드
    list_filter = ('my_current_major',)
    # 필터링 가능한 필드 정의 (현재 소속 전공 기준)



# UserTulink 모델을 Admin에 등록
@admin.register(UserTulink)
class UserTulinkAdmin(admin.ModelAdmin):
    list_display = ('current_major', 'tutoring_major', 'tutoring_sub_major', 'available_days', 'available_times', 'college')  # college 필드 추가
    search_fields = ('current_major', 'tutoring_major', 'tutoring_sub_major', 'college')  # 검색 가능 필드에 college 추가
    list_filter = ('current_major', 'tutoring_major', 'available_days')  # 필요시 필터링 추가



@admin.register(DoTulink)
class DoTulinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'college', 'major', 'sub_major', 'available_times', 'created_at')  # 표시할 필드들
    search_fields = ('user__name', 'college', 'major', 'sub_major')  # 검색 가능 필드
    list_filter = ('college', 'major', 'sub_major', 'available_times')  # 필터 추가




# TutoringRequest 모델을 Admin에 등록
@admin.register(TutoringRequest)  # TutoringRequest 모델 등록
class TutoringRequestAdmin(admin.ModelAdmin):
    list_display = ('tutee_email', 'tutor_email', 'major', 'date', 'time_slot', 'status')
    # 표시할 필드 목록
    search_fields = ('tutee_email__email', 'tutor_email__email', 'major')
    # 튜티 이메일, 튜터 이메일, 요청 전공으로 검색 가능
    list_filter = ('status', 'date')
    # 요청 상태와 날짜를 기준으로 필터링

# Payment 모델을 Admin에 등록
@admin.register(Payment)  # Payment 모델 등록
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'status', 'created_at')
    # 표시할 필드 목록
    search_fields = ('user__email', 'payment_method', 'status')
    # 결제 사용자 이메일, 결제 방식, 상태로 검색 가능
    list_filter = ('status', 'payment_method')
    # 결제 상태와 결제 방식으로 필터링

# Feedback 모델을 Admin에 등록
@admin.register(Feedback)  # Feedback 모델 등록
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('tutoring_request', 'rating', 'created_at')
    # 표시할 필드 목록
    search_fields = ('tutoring_request__tutee_email__email',)
    # 튜티 이메일을 기준으로 검색 가능
    list_filter = ('rating',)
    # 평점을 기준으로 필터링

# Major 모델을 Admin에 등록
@admin.register(Major)  # Major 모델 등록
class MajorAdmin(admin.ModelAdmin):
    list_display = ('major_name', 'sub_major_name', 'created_at')
    # 표시할 필드 목록
    search_fields = ('major_name', 'sub_major_name')
    # 전공명과 세부 전공명으로 검색 가능
    list_filter = ('major_name',)
    # 전공명 기준으로 필터링

# Link 모델을 Admin에 등록
@admin.register(Link)  # Link 모델 등록
class LinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'tutoring_request', 'used_at', 'remaining_links')
    # 표시할 필드 목록
    search_fields = ('user__email',)
    # 사용자 이메일 기준으로 검색 가능
    list_filter = ('used_at',)
    # 사용 날짜 기준으로 필터링
