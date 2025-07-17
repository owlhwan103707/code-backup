from django.db import models



# User Table - 사용자 정보 저장
class UserProfile(models.Model):
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
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # 튜링크 요청한 사용자
    college = models.TextField(null=True, blank=True)  # 단과대학
    major = models.TextField(null=True, blank=True)  # 전공
    sub_major = models.TextField(null=True, blank=True)  # 세부 전공
    available_times = models.TextField(null=True, blank=True)  # 가능 시간대
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시간

    def __str__(self):
        return f"{self.user.name} - {self.college} - {self.major}"





