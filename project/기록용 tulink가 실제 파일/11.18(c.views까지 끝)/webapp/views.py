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
import unicodedata  # 문자열 정규화를 위한 모듈

from django.shortcuts import render, redirect  # HTTP 요청 처리 및 리디렉션 기능 제공
from django.forms import formset_factory  # 동적 폼셋 생성을 위한 모듈
from .models import User, UserTulink, DoTulink  # 데이터베이스 모델 가져오기
from .forms import TutoringMajorForm  # 사용자 입력 폼 가져오기
from django.contrib.auth.decorators import login_required  # 로그인 요구 데코레이터
from datetime import datetime  # 현재 요일 가져오기 위해 필요

from django.db.models import Q #user와 dotulink비교를 위해서


# 데이터 정규화 및 필터링 함수
# 데이터 정규화 및 필터링 함수
def normalize_and_filter_sub_majors(raw_data, prefix):
    """
    데이터 정규화 및 접두어로 필터링
    :param raw_data: 줄바꿈 및 쉼표로 구분된 원본 데이터
    :param prefix: 필터링할 접두어 (e.g., 'a.')
    :return: 접두어로 필터링된 결과 리스트
    """
    print("Raw Tutoring Sub-Major Data:", raw_data)  # 원본 데이터 확인

    # 1. 데이터 정규화 (공백 및 줄바꿈 제거)
    normalized_sub_majors = [
        major.strip()  # 앞뒤 공백 제거
        for line in raw_data.strip().splitlines()  # 줄 단위로 분리
        for major in line.split(",")  # 쉼표 단위로 추가 분리
        if major.strip()  # 빈 값 제외
    ]

    print("Normalized Sub-Majors:", normalized_sub_majors)  # 정규화된 데이터 확인

    # 2. 접두어로 필터링
    filtered_sub_majors = [sub for sub in normalized_sub_majors if sub.startswith(prefix)]
    print("Prefix for Filtering:", prefix)  # 필터링 조건 확인
    print("Filtered Sub-Majors:", filtered_sub_majors)  # 필터링 결과 확인

    return filtered_sub_majors





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
def signup_step3(request):
    """
    회원가입 3단계: 튜터링 가능 요일 및 시간대 선택.
    """
    # --- POST 요청 처리 ---
    if request.method == 'POST':
        # 사용자가 선택한 튜터링 가능 요일 데이터를 리스트로 가져옵니다.
        # 요청 데이터에서 'available_days[]'라는 이름의 필드를 찾아 리스트로 반환합니다.
        available_days = request.POST.getlist('available_days[]')  # 예: ['월', '화']

        # 사용자가 선택한 튜터링 가능 시간대를 저장할 딕셔너리를 초기화합니다.
        # 이 딕셔너리는 각 요일을 키(key)로 하고, 해당 요일의 시간대를 값(value)으로 저장합니다.
        available_times = {}  # 예: {'월': ['10~11', '11~12'], '화': ['13~14']}

        # POST 요청 데이터에서 시간대 필드를 반복적으로 처리합니다.
        # 시간대 데이터는 `available_times[0]`, `available_times[1]` 같은 형식으로 전송됩니다.
        for key, values in request.POST.lists():  # 요청 데이터에서 모든 키와 값을 반복
            if key.startswith('available_times['):  # 키 이름이 'available_times['로 시작하는지 확인
                # `available_times[0]`과 같은 키에서 숫자 인덱스를 추출합니다.
                index = key.split('[')[1].split(']')[0]  # 예: '0', '1'

                # 추출한 인덱스를 사용하여 해당 요일 데이터를 가져옵니다.
                day = available_days[int(index)]  # 예: '월' 또는 '화'

                # 딕셔너리에 해당 요일을 키로 하고, 선택된 시간대를 값으로 저장합니다.
                available_times[day] = values  # 예: {'월': ['10~11', '11~12']}

        # 요일별 시간대 데이터를 하나의 문자열로 변환하여 저장할 준비를 합니다.
        # 각 요일의 시간대는 ','로 구분하고, 요일별 데이터는 '\n'으로 구분합니다.
        times_result = "\n".join(
            [f"{day},{';'.join(times)}" for day, times in available_times.items()]
        )
        # 예: "월,10~11;11~12\n화,13~14"

        # 현재 세션에 로그인한 사용자 ID를 통해 `User` 객체를 가져옵니다.
        # 이 정보는 세션에 'user_id'로 저장되어 있어야 합니다.
        user = User.objects.get(id=request.session['user_id'])

        # 사용자 객체의 `my_available_days` 필드에 선택한 요일 데이터를 저장합니다.
        # 여러 요일을 '\n'으로 구분하여 저장합니다.
        user.my_available_days = "\n".join(available_days)  # 예: "월\n화"

        # 사용자 객체의 `my_available_times` 필드에 변환된 시간대 데이터를 저장합니다.
        user.my_available_times = times_result  # 예: "월,10~11;11~12\n화,13~14"

        # 변경된 사용자 데이터를 데이터베이스에 저장합니다.
        user.save()

        # 저장이 완료되면 메인 페이지로 리디렉션합니다.
        return redirect('webapp:index')

    # --- GET 요청 처리 ---
    elif request.method == 'GET':
        # UserTulink 데이터 가져오기
        tulink_data = UserTulink.objects.first()
        available_times_by_day = {}

        if tulink_data and tulink_data.available_times:
            # 데이터를 줄 단위로 분리
            for entry in tulink_data.available_times.split("\n"):
                day, times = entry.split(":")  # 요일과 시간대를 ":"로 분리
                available_times_by_day[day] = times.split(",")  # 시간대는 쉼표로 분리

        context = {
            'available_days': tulink_data.available_days.split(
                ",") if tulink_data and tulink_data.available_days else [],
            'available_times': available_times_by_day,  # 요일별 시간대 데이터를 전달
        }
        return render(request, 'webapp/signup_step3.html', context)

    # --- 기본 예외 처리 ---
    # POST나 GET 이외의 요청(예: PUT, DELETE)이 발생할 경우 기본적으로 HTML 페이지를 반환합니다.
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
        selected_major = request.POST.get('major')
        tulink_entry.major = selected_major
        tulink_entry.save()

        # 선택된 전공을 세션에 저장
        request.session['selected_major'] = selected_major

        return redirect('webapp:do_tulink2')

    # UserTulink 데이터 가져오기
    tulink_data = UserTulink.objects.first()
    context = {
        'colleges': tulink_data.college.split(",") if tulink_data and tulink_data.college else [],
        'majors': tulink_data.tutoring_major.split("\n") if tulink_data and tulink_data.tutoring_major else [],
    }
    return render(request, 'webapp/do_tulink1.html', context)





# do_tulink2: 서브 전공 선택
def do_tulink2(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.session['user_id'])

        # DoTulink 업데이트
        tulink_entry, created = DoTulink.objects.get_or_create(user=user)
        tulink_entry.sub_major = request.POST.get('sub_major')
        tulink_entry.save()

        return redirect('webapp:do_tulink3')  # 다음 단계로 이동

    # 선택된 전공 가져오기
    selected_major = request.session.get('selected_major')
    if not selected_major:
        print("Error: selected_major is None or empty!")
    else:
        print("Selected Major:", selected_major)

    tulink_data = UserTulink.objects.first()

    # 선택된 전공에 맞는 서브 전공 필터링
    if tulink_data and tulink_data.tutoring_sub_major:
        prefix = selected_major.split(".")[0] + "." if "." in selected_major else selected_major[0]
        print("Prefix for Filtering:", prefix)

        # 데이터를 필터링하는 함수 호출
        filtered_sub_majors = normalize_and_filter_sub_majors(
            raw_data=tulink_data.tutoring_sub_major,
            prefix=prefix
        )
    else:
        filtered_sub_majors = []
        print("Error: tutoring_sub_major is missing or empty!")

    context = {
        'selected_major': selected_major,
        'sub_majors': filtered_sub_majors,
    }
    return render(request, 'webapp/do_tulink2.html', context)




# do_tulink3: 가능 시간대 선택


from datetime import datetime

# do_tulink3: 가능 시간대 선택
from datetime import datetime

def do_tulink3(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.session['user_id'])

        # DoTulink 업데이트
        tulink_entry, created = DoTulink.objects.get_or_create(user=user)

        # 오늘 요일 가져오기 (예: '월', '화', ...)
        today = datetime.now().strftime("%a")  # 'Mon', 'Tue' 형식으로 반환
        korean_days = {
            'Mon': '월', 'Tue': '화', 'Wed': '수',
            'Thu': '목', 'Fri': '금', 'Sat': '토', 'Sun': '일'
        }
        today_korean = korean_days.get(today, 'Unknown')  # 오늘 요일을 한글로 변환

        # 다중 선택된 시간대 리스트 가져오기
        selected_times = request.POST.getlist('available_times')  # getlist로 다중 선택 값 가져오기

        # 첫 번째 시간대에만 요일 추가
        if selected_times:
            combined_available_times = [f"{today_korean},{selected_times[0]}"] + selected_times[1:]
        else:
            combined_available_times = []

        # 세미콜론으로 연결하여 저장
        tulink_entry.available_times = ";".join(combined_available_times)
        tulink_entry.save()

        return redirect('webapp:choice_tulink')

    # UserTulink 데이터 가져오기
    tulink_data = UserTulink.objects.first()
    available_times = []

    # "today:"로 시작하는 줄만 필터링
    if tulink_data and tulink_data.available_times:
        for line in tulink_data.available_times.splitlines():
            if line.startswith("today:"):
                # "today:" 제거하고 숫자 시간대만 추출
                available_times = [
                    time.strip() for time in line.replace("today:", "").split(",") if time.strip()
                ]
                break  # "today:" 줄만 처리하고 나머지는 무시

    context = {
        'available_times': available_times,  # 숫자 시간대 리스트
    }
    return render(request, 'webapp/do_tulink3.html', context)





def choice_tulink(request):

    # User 모델의 모든 데이터를 가져옵니다.
    users = User.objects.all()
    print("유저의 모든 정보들:")
    for user in users:
        print(user)

    # 최신 DoTulink 레코드 하나 가져오기
    latest_record = DoTulink.objects.order_by('-created_at').first()
    if not latest_record:
        print("Dotulink 테이블이 비어 있습니다.")
        return render(request, 'webapp/choice_tulink.html', {'users': users})

    print("Dotulink의 마지막 테이블:", latest_record)




    # Major, Sub Major, Available Times를 나누기
    major_parts = latest_record.major.split(';') if latest_record.major else []
    sub_major_parts = latest_record.sub_major.split(';') if latest_record.sub_major else []
    time_parts = latest_record.available_times.split(';') if latest_record.available_times else []

    # 매칭 로직
    matching_users = User.objects.filter(
        Q(my_tutoring_major__icontains=latest_record.major) |  # Major의 일부분이라도 포함된 경우
        Q(my_tutoring_sub_major__icontains=latest_record.sub_major)  # Sub Major의 일부분이라도 포함된 경우
    ).distinct()

    # 시간대 매칭
    # 시간대 매칭
    final_users = []
    for user in matching_users:
        user_times = user.my_available_times.split(';')  # 유저 시간대 분리
        if any(latest_time.strip() in user_time.strip() for latest_time in time_parts for user_time in user_times):
            final_users.append(user)  # 겹치는 경우 유저 추가

    print("매칭된 유저들:")
    for user in final_users:
        print(user)

    context = {
        'users': users,
        'latest_record': latest_record,
        'matching_users': final_users,
    }
    return render(request, 'webapp/choice_tulink.html', context)
