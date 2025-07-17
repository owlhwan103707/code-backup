from django.contrib import admin
from .models import User, UserTulink, TutoringRequest, Payment, Feedback, Major, Link

# User 모델을 Admin에 등록
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'my_current_major', 'my_tutoring_major', 'my_available_days')
    search_fields = ('name', 'email', 'my_current_major')
    list_filter = ('my_current_major',)  # 필터링 옵션 추가


# UserTulink 모델을 Admin에 등록
@admin.register(UserTulink)
class UserTulinkAdmin(admin.ModelAdmin):
    list_display = ('current_major', 'tutoring_major', 'tutoring_sub_major', 'available_days', 'available_times')
    search_fields = ('current_major', 'tutoring_major', 'tutoring_sub_major')
    list_filter = ('current_major', 'tutoring_major', 'available_days')  # 필터링 옵션 추가


# TutoringRequest 모델을 Admin에 등록
@admin.register(TutoringRequest)
class TutoringRequestAdmin(admin.ModelAdmin):
    list_display = ('tutee_email', 'tutor_email', 'major', 'date', 'time_slot', 'status')
    search_fields = ('tutee_email__email', 'tutor_email__email', 'major')
    list_filter = ('status', 'date')


# Payment 모델을 Admin에 등록
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'status', 'created_at')
    search_fields = ('user__email', 'payment_method', 'status')
    list_filter = ('status', 'payment_method')


# Feedback 모델을 Admin에 등록
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('tutoring_request', 'rating', 'created_at')
    search_fields = ('tutoring_request__tutee_email__email',)
    list_filter = ('rating',)


# Major 모델을 Admin에 등록
@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ('major_name', 'sub_major_name', 'created_at')
    search_fields = ('major_name', 'sub_major_name')
    list_filter = ('major_name',)


# Link 모델을 Admin에 등록
@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'tutoring_request', 'used_at', 'remaining_links')
    search_fields = ('user__email',)
    list_filter = ('used_at',)
