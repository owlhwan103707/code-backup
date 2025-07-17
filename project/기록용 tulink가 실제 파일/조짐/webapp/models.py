from django.db import models

# User Table - 사용자 정보 저장
class User(models.Model):
    id = models.AutoField(primary_key=True)  # 자동 생성 ID
    name = models.CharField(max_length=100)  # 사용자 이름
    email = models.EmailField(unique=True)  # 이메일 (고유 식별자)
    password = models.CharField(max_length=100)  # 비밀번호
    my_current_major = models.CharField(max_length=100)  # 현재 소속 전공
    my_tutoring_major = models.CharField(max_length=100)  # 튜터링할 전공
    my_tutoring_sub_major = models.CharField(max_length=100, null=True, blank=True)  # 튜터링할 세부 전공
    my_available_days = models.TextField()  # 가능 요일
    my_available_times = models.TextField()  # 가능 시간대

    def __str__(self):
        return self.email  # 객체 출력 시 이메일을 표시




# UserTulink Table - 전공, 요일, 시간 등의 선택 항목 데이터 저장
class UserTulink(models.Model):
    current_major = models.TextField()  # 현재 소속 전공
    tutoring_major = models.TextField()  # 튜터링할 전공
    tutoring_sub_major = models.TextField(null=True, blank=True)  # 튜터링할 세부 전공
    available_days = models.TextField()  # 가능 요일
    available_times = models.TextField()  # 가능 시간대
    college = models.TextField(null=True, blank=True)  # 단과대학 필드 추가 (TextField)

    def __str__(self):
        return f"{self.current_major} - {self.tutoring_major}"


class DoTulink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 튜링크 요청한 사용자
    college = models.TextField(null=True, blank=True)  # 단과대학
    major = models.TextField(null=True, blank=True)  # 전공
    sub_major = models.TextField(null=True, blank=True)  # 세부 전공
    available_times = models.TextField(null=True, blank=True)  # 가능 시간대
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시간

    def __str__(self):
        return f"{self.user.name} - {self.college} - {self.major}"






# TutoringRequests Table - 튜터링 요청 정보를 저장하는 테이블
class TutoringRequest(models.Model):
    tutee_email = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='tutee_requests')  # 튜티의 이메일 (외래키, User 참조)
    tutor_email = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='tutor_requests')  # 튜터의 이메일 (외래키, User 참조)
    major = models.CharField(max_length=100)  # 요청한 전공
    sub_major = models.CharField(max_length=100)  # 요청한 세부 전공
    date = models.DateField()  # 튜터링 요청 날짜
    time_slot = models.TimeField()  # 튜터링 요청 시간대
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'),
                                                      ('Declined', 'Declined')])  # 요청 상태
    created_at = models.DateTimeField(auto_now_add=True)  # 요청 생성 시간
    updated_at = models.DateTimeField(auto_now=True)  # 요청 마지막 수정 시간


# Payments Table - 결제 정보를 저장하는 테이블
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 결제한 사용자 (외래키, User 참조)
    amount = models.FloatField()  # 결제 금액
    link_count = models.IntegerField()  # 구매한 링크 개수
    payment_method = models.CharField(max_length=50)  # 결제 방식 (예: KakaoPay, 카드 등)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'),
                                                      ('Failed', 'Failed')])  # 결제 상태
    created_at = models.DateTimeField(auto_now_add=True)  # 결제 시간


# Feedback Table - 튜터링 피드백 정보를 저장하는 테이블
class Feedback(models.Model):
    tutoring_request = models.ForeignKey(TutoringRequest,
                                         on_delete=models.CASCADE)  # 튜터링 요청 정보 (외래키, TutoringRequest 참조)
    rating = models.FloatField()  # 튜티가 준 평점
    comments = models.TextField(null=True, blank=True)  # 추가 코멘트 (선택적)
    created_at = models.DateTimeField(auto_now_add=True)  # 피드백 작성 시간


# Majors Table - 전공 정보를 저장하는 테이블
class Major(models.Model):
    major_name = models.CharField(max_length=100)  # 전공 이름
    sub_major_name = models.CharField(max_length=100, null=True, blank=True)  # 세부 전공 이름
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    def __str__(self):
        return f"{self.major_name} - {self.sub_major_name}" if self.sub_major_name else self.major_name


# Links Table - 링크 정보를 저장하는 테이블
class Link(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 링크를 사용하는 사용자 (외래키, User 참조)
    tutoring_request = models.ForeignKey(TutoringRequest, on_delete=models.SET_NULL, null=True,
                                         blank=True)  # 관련된 튜터링 요청 (선택적, 외래키)
    used_at = models.DateTimeField(null=True, blank=True)  # 링크 사용 시간 (선택적)
    remaining_links = models.IntegerField()  # 남은 링크 개수
