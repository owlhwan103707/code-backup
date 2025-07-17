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

from django.shortcuts import render, redirect  # HTTP 요청 처리 및 리디렉션 기능
from django.forms import formset_factory  # 동적 폼셋 생성
from .models import User, UserTulink  # User 및 UserTulink 모델 가져오기
from .forms import TutoringMajorForm  # TutoringMajorForm 폼 가져오기

# 메인 페이지 뷰
def index(request):
    """
    메인 페이지를 렌더링합니다.
    """
    return render(request, 'webapp/index.html')


# 로그인 페이지 뷰
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # 데이터베이스에서 사용자 검색
            user = User.objects.get(email=email, password=password)
            # 로그인 성공 시 세션에 사용자 정보 저장
            request.session['user_id'] = user.id
            return render(request, 'webapp/after_login.html', {'user_name': user.name})
        except User.DoesNotExist:
            # 로그인 실패 시 에러 메시지와 함께 다시 로그인 페이지 렌더링
            return render(request, 'webapp/login.html', {'error_message': 'Invalid email or password.'})

    return render(request, 'webapp/login.html')


# Step 1: 별명, 이메일, 비밀번호 입력
def signup_step1(request):
    """
    회원가입 1단계: 사용자 별명, 이메일, 비밀번호 입력 및 저장.
    """
    if request.method == "POST":
        # User 테이블에 데이터를 저장합니다.
        user = User.objects.create(
            name=request.POST['name'],  # 사용자가 입력한 이름
            email=request.POST['email'],  # 사용자가 입력한 이메일
            password=request.POST['password'],  # 사용자가 입력한 비밀번호 (암호화 필요)
        )
        # 세션에 사용자 ID 저장
        request.session['user_id'] = user.id
        # 2단계로 리디렉션
        return redirect('webapp:signup_step2')

    # GET 요청 시 회원가입 1단계 템플릿 렌더링
    return render(request, 'webapp/signup_step1.html')


# Step 2: 현재 소속 전공, 튜터링할 전공, 세부 전공 입력
def signup_step2(request):
    """
    회원가입 2단계: 현재 소속 전공, 튜터링할 전공 및 세부 전공 선택.
    """
    if request.method == 'POST':
        # 세션에서 user_id 가져오기
        user_id = request.session.get('user_id')
        if not user_id:  # user_id가 없으면 1단계로 리디렉션
            return redirect('webapp:signup_step1')

        # User 객체 가져오기
        user = User.objects.get(id=user_id)

        # 현재 소속 전공 저장
        user.my_current_major = request.POST.get('current_major')

        # 튜터링 전공 및 세부 전공 저장
        tutoring_majors = request.POST.getlist('tutoring_major[]')  # POST 데이터에서 전공 리스트 가져오기
        tutoring_sub_majors = request.POST.getlist('tutoring_sub_major[]')  # POST 데이터에서 세부 전공 리스트 가져오기

        # 데이터를 세미콜론으로 구분해 저장
        user.my_tutoring_major = ";".join(tutoring_majors)
        user.my_tutoring_sub_major = ";".join(tutoring_sub_majors)
        user.save()

        # 3단계로 리디렉션
        return redirect('webapp:signup_step3')

    # GET 요청 시 UserTulink 데이터를 가져와 드롭다운 옵션으로 제공
    tulink_data = UserTulink.objects.first()  # UserTulink 테이블에서 첫 번째 데이터 가져오기
    if not tulink_data:  # 데이터가 없으면 에러 페이지 렌더링
        return render(request, 'webapp/error.html', {'message': 'UserTulink 데이터가 없습니다.'})

    # 드롭다운 메뉴 옵션으로 제공할 데이터를 준비
    context = {
        'current_majors': tulink_data.current_major.split(","),  # 현재 소속 전공
        'tutoring_majors': tulink_data.tutoring_major.split(","),  # 튜터링할 전공
        'sub_majors': tulink_data.tutoring_sub_major.split(",") if tulink_data.tutoring_sub_major else [],  # 튜터링 세부 전공
    }
    return render(request, 'webapp/signup_step2.html', context)


# Step 3: 튜터링 가능 요일, 가능 시간대 입력
def signup_step3(request):
    """
    회원가입 3단계: 튜터링 가능 요일 및 시간대 선택.
    """
    if request.method == 'POST':
        # POST 데이터에서 선택된 요일과 시간대를 가져오기
        available_days = request.POST.getlist('available_days[]')
        available_times = request.POST.getlist('available_times[]')

        # 세션에서 user_id를 사용해 User 객체 가져오기
        user = User.objects.get(id=request.session['user_id'])
        # 데이터를 세미콜론으로 구분해 저장
        user.my_available_days = ";".join(available_days)
        user.my_available_times = ";".join(available_times)
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

    # 기본적으로 템플릿 렌더링 (예외 처리)
    return render(request, 'webapp/signup_step3.html', {})
