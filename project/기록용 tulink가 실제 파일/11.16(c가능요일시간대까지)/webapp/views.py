"""
웹 애플리케이션의 뷰 로직을 정의하는 파일입니다.
이 코드는 사용자의 요청(request)을 처리하고 적절한 HTML 파일을 렌더링하거나, 데이터베이스와 상호작용하여 데이터를 저장/수정합니다.

연관된 파일:
- `models.py`: 데이터베이스 테이블을 정의한 모델 파일
- `forms.py`: 사용자 입력을 처리하는 폼 정의
- `urls.py`: 각 뷰와 연결된 URL 패턴 정의
- HTML 템플릿 파일들: `templates/webapp/` 폴더에 위치한 템플릿 (e.g., `signup_step1.html`, `signup_step2.html`, `signup_step3.html`)

이 파일은 다음과 같은 뷰를 제공합니다:
1. `index`: 메인 페이지
2. `login_view`: 로그인 페이지
3. `signup_step1`: 회원가입 1단계 (별명, 이메일, 비밀번호 입력)
4. `signup_step2`: 회원가입 2단계 (전공 및 세부 정보 입력)
5. `signup_step3`: 회원가입 3단계 (가능 요일 및 시간대 입력)
"""


from django.shortcuts import render, redirect  # HTTP 요청 처리 및 리디렉션 기능 제공
from django.forms import formset_factory  # 동적 폼셋 생성을 위한 모듈
from .models import User, UserTulink, DoTulink  # 데이터베이스 모델 가져오기
from .forms import TutoringMajorForm  # 사용자 입력 폼 가져오기
from django.contrib.auth.decorators import login_required  # 로그인 요구 데코레이터



# 메인 페이지 뷰
def index(request):
    """
    메인 페이지를 렌더링하는 함수.
    """
    return render(request, 'webapp/index.html')  # index.html 템플릿 렌더링


# 로그인 페이지 뷰
def login_view(request):
    if request.method == "POST":  # POST 요청: 로그인 처리
        email = request.POST.get('email')  # 사용자 입력 이메일
        password = request.POST.get('password')  # 사용자 입력 비밀번호

        try:
            # 데이터베이스에서 해당 이메일과 비밀번호가 일치하는 사용자 검색
            user = User.objects.get(email=email, password=password)
            # 로그인 성공 시 세션에 사용자 ID 저장
            request.session['user_id'] = user.id
            return render(request, 'webapp/after_login.html', {'user_name': user.name})  # 로그인 성공 후 페이지 이동
        except User.DoesNotExist:
            # 로그인 실패 시 에러 메시지와 함께 다시 로그인 페이지 렌더링
            return render(request, 'webapp/login.html', {'error_message': 'Invalid email or password.'})

    return render(request, 'webapp/login.html')  # GET 요청: 로그인 폼 렌더링




# Step 1: 별명, 이메일, 비밀번호 입력
def signup_step1(request):
    """
    회원가입 1단계: 사용자 기본 정보를 입력받아 저장.
    """
    if request.method == "POST":  # POST 요청 처리
        user = User.objects.create(
            name=request.POST['name'],  # 사용자 이름
            email=request.POST['email'],  # 사용자 이메일
            password=request.POST['password'],  # 사용자 비밀번호
        )
        request.session['user_id'] = user.id  # 사용자 ID를 세션에 저장
        return redirect('webapp:signup_step2')  # 회원가입 2단계로 이동

    return render(request, 'webapp/signup_step1.html')  # GET 요청: 회원가입 1단계 폼 렌더링



# Step 2: 현재 소속 전공, 튜터링할 전공, 세부 전공 입력
# signup_step2 뷰에서 드롭다운 데이터를 쉼표로 구분
def signup_step2(request):
    """
    회원가입 2단계: 현재 소속 전공, 튜터링할 전공 및 세부 전공 선택
    """
    if request.method == 'POST':
        # 세션에서 user_id 가져오기
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('webapp:signup_step1')

        # User 객체 가져오기
        user = User.objects.get(id=user_id)

        # 현재 소속 전공 저장
        user.my_current_major = request.POST.get('current_major')

        # 튜터링 전공 및 세부 전공 저장
        tutoring_majors = request.POST.getlist('tutoring_major[]')
        tutoring_sub_majors = request.POST.getlist('tutoring_sub_major[]')

        # 데이터를 세미콜론으로 저장
        user.my_tutoring_major = ";".join(tutoring_majors)
        user.my_tutoring_sub_major = ";".join(tutoring_sub_majors)
        user.save()

        # 다음 단계로 이동
        return redirect('webapp:signup_step3')

    # GET 요청 처리
    tulink_data = UserTulink.objects.first()
    if not tulink_data:
        return render(request, 'webapp/error.html', {'message': 'UserTulink 데이터가 없습니다.'})

    # 전공과 세부 전공을 매칭
    tutoring_data = {}
    major_lines = tulink_data.tutoring_major.split("\n")
    sub_major_lines = tulink_data.tutoring_sub_major.split("\n")

    for major_line, sub_major_line in zip(major_lines, sub_major_lines):
        major_key = major_line.split(",")[0].strip()
        sub_major_values = sub_major_line.split(",")
        tutoring_data[major_key] = [sub.strip() for sub in sub_major_values]

    context = {
        'current_majors': tulink_data.current_major.split(","),
        'tutoring_data': tutoring_data,  # 전공과 세부 전공 매칭 데이터
    }
    return render(request, 'webapp/signup_step2.html', context)




# Step 3: 튜터링 가능 요일, 가능 시간대 입력

# Step 3: 튜터링 가능 요일, 가능 시간대 입력
def signup_step3(request):
    """
    회원가입 3단계: 튜터링 가능 요일 및 시간대 선택.
    """
    if request.method == 'POST':
        # POST 요청에서 선택된 요일과 시간대 가져오기
        available_days = request.POST.getlist('available_days[]')  # 요일 리스트
        available_times = request.POST.getlist('available_times[]')  # 시간대 리스트

        # 세션에서 user_id를 사용해 User 객체 가져오기
        user = User.objects.get(id=request.session['user_id'])

        # 요일과 시간 데이터를 각각 저장
        user.my_available_days = "\n".join(available_days)  # 요일은 my_available_days 필드에 저장
        user.my_available_times = ";".join(available_times)  # 시간은 my_available_times 필드에 저장
        user.save()

        # 가입 완료 후 메인 페이지로 리디렉션
        return redirect('webapp:index')

    elif request.method == 'GET':
        # GET 요청 시 UserTulink 데이터를 가져와 드롭다운 옵션으로 제공
        tulink_data = UserTulink.objects.first()
        context = {
            'available_days': tulink_data.available_days.split(","),  # 가능한 요일
            'available_times': tulink_data.available_times.split(","),  # 가능한 시간대
        }
        return render(request, 'webapp/signup_step3.html', context)

    # 기본 예외 처리
    return render(request, 'webapp/signup_step3.html', {})









# 로그아웃 뷰
def logout_view(request):
    # 세션 정보 삭제
    request.session.flush()
    return redirect('webapp:index')  # 로그아웃 후 메인 페이지로 이동





# 마이페이지 뷰
def mypage_view(request):
    """
    마이페이지: 로그인한 사용자가 입력한 정보들을 확인.
    """
    user_id = request.session.get('user_id')  # 세션에서 사용자 ID 가져오기
    if not user_id:  # 사용자 ID가 없으면 로그인 페이지로 리디렉션
        return redirect('webapp:login_view')

    user = User.objects.get(id=user_id)  # 데이터베이스에서 사용자 객체 가져오기

    # 사용자 데이터를 템플릿에 전달
    context = {
        'user_name': user.name,  # 사용자 이름
        'user_email': user.email,  # 사용자 이메일
        'user_major': user.my_current_major,  # 현재 소속 전공
        'user_tutoring_major': user.my_tutoring_major,  # 튜터링할 전공
        'user_available_days': user.my_available_days,  # 가능한 요일
        'user_available_times': user.my_available_times,  # 가능한 시간대
    }

    return render(request, 'webapp/mypage.html', context)  # mypage.html 템플릿 렌더링






# after_login_view: 로그인 후 사용자 환영 페이지
def after_login_view(request):
    """
    로그인 이후 사용자 환영 페이지를 렌더링.
    """
    user_id = request.session.get('user_id')  # 세션에서 사용자 ID 가져오기
    if not user_id:  # 사용자 ID가 없으면 로그인 페이지로 리디렉션
        return redirect('webapp:login_view')

    user = User.objects.get(id=user_id)  # 데이터베이스에서 사용자 객체 가져오기
    context = {
        'user_name': user.name,  # 사용자 이름 전달
    }
    return render(request, 'webapp/after_login.html', context)  # after_login.html 템플릿 렌더링



# do_tulink1: 단과대학 및 튜터링 전공 선택
def do_tulink1(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.session['user_id'])

        # DoTulink 생성 또는 업데이트
        tulink_entry, created = DoTulink.objects.get_or_create(user=user)
        tulink_entry.college = request.POST.get('college')
        tulink_entry.major = request.POST.get('major')
        tulink_entry.save()

        return redirect('webapp:do_tulink2')

    # UserTulink 데이터 가져오기
    tulink_data = UserTulink.objects.first()
    context = {
        'colleges': tulink_data.college.split(",") if tulink_data and tulink_data.college else [],
        'majors': tulink_data.tutoring_major.split(",") if tulink_data and tulink_data.tutoring_major else [],
    }
    return render(request, 'webapp/do_tulink1.html', context)


# do_tulink2: 세부 전공 선택
def do_tulink2(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.session['user_id'])

        # DoTulink 업데이트
        tulink_entry = DoTulink.objects.get(user=user)
        tulink_entry.sub_major = request.POST.get('sub_major')
        tulink_entry.save()

        return redirect('webapp:do_tulink3')

    # UserTulink 데이터 가져오기
    tulink_data = UserTulink.objects.first()
    context = {
        'sub_majors': tulink_data.tutoring_sub_major.split(",") if tulink_data and tulink_data.tutoring_sub_major else [],
    }
    return render(request, 'webapp/do_tulink2.html', context)


# do_tulink3: 가능 시간대 선택
def do_tulink3(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.session['user_id'])

        # DoTulink 업데이트
        tulink_entry = DoTulink.objects.get(user=user)
        tulink_entry.available_times = request.POST.get('available_times')
        tulink_entry.save()

        return redirect('webapp:choice_tulink')

    # UserTulink 데이터 가져오기
    tulink_data = UserTulink.objects.first()
    context = {
        'available_times': tulink_data.available_times.split(",") if tulink_data and tulink_data.available_times else [],
    }
    return render(request, 'webapp/do_tulink3.html', context)


# 선택 완료 페이지
def choice_tulink(request):
    user = User.objects.get(id=request.session['user_id'])
    tulink_entry = DoTulink.objects.get(user=user)

    context = {
        'tulink_entry': tulink_entry,
    }
    return render(request, 'webapp/choice_tulink.html', context)
