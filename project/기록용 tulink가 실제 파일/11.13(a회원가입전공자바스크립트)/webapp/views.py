from django.shortcuts import render, redirect
from django.forms import formset_factory
from .models import User, UserTulink
from .forms import TutoringMajorForm

# 메인 페이지 뷰
def index(request):
    context = {'message': '아 나이스 11월 4일 오지환.'}
    return render(request, 'webapp/index.html', context)


# 서비스 페이지 뷰
def service(request):
    lst = []
    lst.append('자정 인지')
    lst.append('인터넷 기술에 대한 이해')
    lst.append('도메인 지식')
    lst.append('사용자경험에 대한 이해')
    lst.append('프로젝트 관리에 대한 이해')
    lst.append('시간관리 능력')
    lst.append('협상 능력')

    context = {'service': lst}
    return render(request, 'webapp/service.html', context)


# 로그인 페이지 뷰
def login_view(request):
    return render(request, 'webapp/login.html')


# Step 1: 별명, 이메일, 비밀번호 입력
def signup_step1(request):
    if request.method == "POST":
        # User 테이블에 데이터 저장
        user = User.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            password=request.POST['password'],  # 비밀번호는 해시 처리 필요
        )
        # 세션에 user_id 저장
        request.session['user_id'] = user.id
        return redirect('webapp:signup_step2')
    return render(request, 'webapp/signup_step1.html')


# Step 2: 현재 소속 전공, 튜터링할 전공, 세부 전공 입력
def signup_step2(request):
    if request.method == 'POST':
        # 세션에서 user_id 가져오기
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('webapp:signup_step1')

        # User 객체 가져오기
        user = User.objects.get(id=user_id)

        # Current Major 저장
        user.my_current_major = request.POST.get('current_major')

        # Tutoring Majors 저장
        tutoring_majors = request.POST.getlist('tutoring_major[]')
        tutoring_sub_majors = request.POST.getlist('tutoring_sub_major[]')

        # 전공 정보를 세미콜론으로 구분해 저장
        user.my_tutoring_major = ";".join(tutoring_majors)
        user.my_tutoring_sub_major = ";".join(tutoring_sub_majors)
        user.save()

        return redirect('webapp:signup_step3')

    # UserTulink 데이터를 가져와 드롭다운 옵션으로 제공
    tulink_data = UserTulink.objects.first()
    if not tulink_data:
        return render(request, 'webapp/error.html', {'message': 'UserTulink 데이터가 없습니다.'})

    context = {
        'current_majors': tulink_data.current_major.split(","),
        'tutoring_majors': tulink_data.tutoring_major.split(","),
        'sub_majors': tulink_data.tutoring_sub_major.split(",") if tulink_data.tutoring_sub_major else [],
    }
    return render(request, 'webapp/signup_step2.html', context)


# Step 3: 튜터링 가능 요일, 가능 시간대 입력
def signup_step3(request):
    if request.method == 'POST':
        # POST 데이터 처리
        available_days = request.POST.getlist('available_days')  # 여러 선택 가능
        available_times = request.POST.getlist('available_times')  # 여러 선택 가능

        # 세션에 저장된 user_id로 User 테이블 업데이트
        user = User.objects.get(id=request.session['user_id'])
        user.my_available_days = ", ".join(available_days)  # 선택된 요일들을 저장
        user.my_available_times = ", ".join(available_times)  # 선택된 시간대를 저장
        user.save()

        # 가입 완료 후 메인 페이지로 이동
        return redirect('webapp:index')

    elif request.method == 'GET':
        # GET 요청 처리: UserTulink에서 선택 항목 가져오기
        try:
            tulink_data = UserTulink.objects.first()  # UserTulink 테이블에서 첫 번째 데이터 가져오기
            context = {
                'available_days': tulink_data.available_days.split(","),
                'available_times': tulink_data.available_times.split(","),
            }
        except AttributeError:
            # UserTulink에 데이터가 없을 경우 기본값 설정
            context = {
                'available_days': ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"],
                'available_times': ["09:00-10:00", "10:00-11:00", "11:00-12:00", "13:00-14:00"],
            }

        # signup_step3.html 렌더링
        return render(request, 'webapp/signup_step3.html', context)

    # 마지막으로 모든 경우를 처리하지 않으면 명시적으로 오류를 반환
    return render(request, 'webapp/signup_step3.html', {})
