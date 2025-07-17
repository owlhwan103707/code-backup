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


11.22
11.25
11.26
11.28수정1
"""
import unicodedata  # 문자열 정규화를 위한 모듈

from django.shortcuts import render, redirect, get_object_or_404  # HTTP 요청 처리 및 리디렉션 기능 제공
from django.forms import formset_factory  # 동적 폼셋 생성을 위한 모듈
from .models import User, UserTulink, DoTulink, UserUsageCount, UserLink  # 데이터베이스 모델 가져오기
from .forms import TutoringMajorForm  # 사용자 입력 폼 가져오기
from django.contrib.auth.decorators import login_required  # 로그인 요구 데코레이터
from datetime import datetime  # 현재 요일 가져오기 위해 필요

from django.db.models import Q #user와 dotulink비교를 위해서
from django.http import HttpResponse #신청하기 모달창


#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------




# 데이터 정규화 및 필터링 함수
# do_tulink2에서 사용하기 위함
def normalize_and_filter_sub_majors(raw_data, prefix):
    """
    데이터 정규화 및 접두어로 필터링
    :param raw_data: 줄바꿈 및 쉼표로 구분된 원본 데이터 (e.g., "a.전공1, a.전공2\nb.전공3, b.전공4")
    :param prefix: 필터링할 접두어 (e.g., 'a.')
    :return: 접두어로 필터링된 결과 리스트
    """

    # --- 디버깅용 출력 ---
    print("Raw Tutoring Sub-Major Data:", raw_data)  # 원본 데이터 확인

    # 1. 데이터 정규화 (공백 및 줄바꿈 제거)
    normalized_sub_majors = [
        major.strip()  # 각 항목의 앞뒤 공백 제거
        for line in raw_data.strip().splitlines()  # 줄바꿈 기준으로 데이터를 분리
        for major in line.split(",")  # 쉼표 기준으로 데이터를 추가로 분리
        if major.strip()  # 공백만 있거나 빈 값은 제외
    ]

    # --- 디버깅용 출력 ---
    print("Normalized Sub-Majors:", normalized_sub_majors)  # 정규화된 데이터 확인

    # 2. 접두어로 필터링
    filtered_sub_majors = [
        sub for sub in normalized_sub_majors  # 정규화된 데이터 항목을 하나씩 검사
        if sub.startswith(prefix)  # 접두어(prefix)로 시작하는 항목만 필터링
    ]

    # --- 디버깅용 출력 ---
    print("Prefix for Filtering:", prefix)  # 필터링 조건 확인
    print("Filtered Sub-Majors:", filtered_sub_majors)  # 필터링 결과 확인

    return filtered_sub_majors  # 필터링된 결과 리스트를 반환


#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------



# 메인 페이지 뷰
def index(request):
    """
    메인 페이지를 렌더링하는 함수.
    """
    return render(request, 'webapp/index.html')  # index.html 템플릿 렌더링


#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------


# 로그인 페이지 뷰
def login_view(request):
    """
    로그인 페이지를 처리하는 뷰 함수
    """
    if request.method == "POST":  # POST 요청: 사용자가 로그인 폼을 제출한 경우
        # 1. 사용자가 입력한 이메일과 비밀번호를 가져옴
        email = request.POST.get('email')  # 폼에서 'email' 필드 값 추출
        password = request.POST.get('password')  # 폼에서 'password' 필드 값 추출

        try:
            # 2. 데이터베이스에서 해당 이메일과 비밀번호를 가진 사용자 검색
            user = User.objects.get(email=email, password=password)

            # --- 디버깅용 출력 ---
            print(f"Login successful for user: {user.name} (ID: {user.id})")

            # 3. 사용자가 존재하면 세션에 사용자 ID를 저장
            request.session['user_id'] = user.id  # 세션에 로그인된 사용자 ID 저장

            # 4. 로그인 성공 페이지 렌더링
            return render(request, 'webapp/after_login.html', {'user_name': user.name})

        except User.DoesNotExist:
            # 5. 데이터베이스에 사용자가 없으면 예외 발생
            # --- 디버깅용 출력 ---
            print(f"Login failed for email: {email}")

            # 6. 로그인 실패 시 에러 메시지를 포함하여 로그인 페이지 다시 렌더링
            return render(request, 'webapp/login.html', {'error_message': 'Invalid email or password.'})

    # GET 요청: 로그인 페이지 렌더링
    return render(request, 'webapp/login.html')  # 로그인 폼 HTML 렌더링


#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------


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



#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------




def signup_step2(request):
    """
    회원가입 2단계: 현재 소속 전공, 튜터링할 전공 및 세부 전공 선택
    """
    # --- POST 요청 처리 ---
    if request.method == 'POST':
        # 세션에서 user_id 가져오기
        user_id = request.session.get('user_id')  # 로그인된 사용자의 ID를 세션에서 가져옵니다.

        if not user_id:  # 만약 세션에 user_id가 없다면, 즉 로그인이 되어 있지 않으면
            return redirect('webapp:signup_step1')  # 1단계 페이지로 리디렉션합니다.

        # User 객체 가져오기
        user = User.objects.get(id=user_id)  # 로그인된 사용자의 User 객체를 데이터베이스에서 가져옵니다.

        # 현재 소속 전공 저장
        user.my_current_major = request.POST.get('current_major')  # 사용자가 선택한 현재 소속 전공을 가져옵니다.

        # 튜터링 전공 및 세부 전공 저장
        tutoring_majors = request.POST.getlist('tutoring_major[]')  # 사용자가 선택한 튜터링 전공을 리스트로 가져옵니다.
        tutoring_sub_majors = request.POST.getlist('tutoring_sub_major[]')  # 사용자가 선택한 튜터링 세부 전공을 리스트로 가져옵니다.

        # 데이터를 세미콜론으로 구분하여 저장
        user.my_tutoring_major = ";".join(tutoring_majors)  # 튜터링 전공을 세미콜론으로 구분하여 저장합니다.
        user.my_tutoring_sub_major = ";".join(tutoring_sub_majors)  # 튜터링 세부 전공을 세미콜론으로 구분하여 저장합니다.

        user.save()  # 변경된 User 객체를 데이터베이스에 저장합니다.

        # --- 다음 단계로 이동 ---
        return redirect('webapp:signup_step3')  # 3단계 페이지로 리디렉션합니다.

    # --- GET 요청 처리 ---
    elif request.method == 'GET':
        # UserTulink 데이터 가져오기
        tulink_data = UserTulink.objects.first()  # UserTulink 객체에서 첫 번째 데이터를 가져옵니다.

        if not tulink_data:  # 만약 UserTulink 데이터가 없다면
            return render(request, 'webapp/error.html', {'message': 'UserTulink 데이터가 없습니다.'})  # 오류 메시지를 띄웁니다.

        # 전공과 세부 전공을 매칭
        tutoring_data = {}  # 튜터링 전공과 세부 전공을 매칭하기 위한 딕셔너리입니다.

        # 튜터링 전공과 세부 전공 데이터를 줄 단위로 분리하여 처리합니다.
        major_lines = tulink_data.tutoring_major.split("\n")  # 튜터링 전공 데이터를 줄 단위로 나눕니다.
        sub_major_lines = tulink_data.tutoring_sub_major.split("\n")  # 튜터링 세부 전공 데이터를 줄 단위로 나눕니다.

        for major_line, sub_major_line in zip(major_lines, sub_major_lines):  # 전공과 세부 전공을 한 줄씩 매칭합니다.
            major_key = major_line.split(",")[0].strip()  # 전공 이름을 구분하여 가져옵니다.
            sub_major_values = sub_major_line.split(",")  # 해당 전공에 대한 세부 전공을 가져옵니다.
            tutoring_data[major_key] = [sub.strip() for sub in sub_major_values]  # 전공과 세부 전공을 튜터링 데이터로 저장합니다.

        # 컨텍스트에 데이터를 담아서 템플릿에 전달합니다.
        context = {
            'current_majors': tulink_data.current_major.split(","),  # 전공을 쉼표로 나누어 리스트로 전달합니다.
            'tutoring_data': tutoring_data,  # 튜터링 전공과 세부 전공 매칭 데이터를 전달합니다.
        }

        return render(request, 'webapp/signup_step2.html', context)  # signup_step2.html 템플릿을 렌더링합니다.


#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------



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



#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------




# 로그아웃 뷰
def logout_view(request):
    # 세션 정보 삭제
    request.session.flush()
    return redirect('webapp:index')  # 로그아웃 후 메인 페이지로 이동



#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------





# after_login_view: 로그인 후 사용자 환영 페이지
def after_login_view(request):
    """
    로그인 이후 사용자 환영 페이지를 렌더링.
    """
    # 1. 세션에서 사용자 ID 가져오기
    user_id = request.session.get('user_id')  # 로그인 시 저장된 세션 값
    if not user_id:  # 사용자 ID가 없으면
        # 2. 로그인이 필요하므로 로그인 페이지로 리디렉션
        return redirect('webapp:login_view')

    # 3. 데이터베이스에서 사용자 ID로 사용자 객체 가져오기
    user = User.objects.get(id=user_id)  # User 모델에서 사용자 정보 검색

    # 4. 템플릿에 전달할 컨텍스트 생성
    context = {
        'user_name': user.name,  # 사용자 이름
    }

    # 5. after_login.html 템플릿을 렌더링하고 사용자 이름 표시
    return render(request, 'webapp/after_login.html', context)




#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------





# do_tulink1: 단과대학 및 튜터링 전공 선택
def do_tulink1(request):
    """
    단과대학 및 전공 선택 페이지
    - POST 요청: 사용자가 선택한 단과대학과 전공 데이터를 저장.
    - GET 요청: 선택 가능한 단과대학과 전공 데이터를 템플릿에 전달.
    """
    if request.method == 'POST':  # POST 요청 처리
        # 세션에서 현재 로그인된 사용자 ID를 가져오고, User 객체를 조회
        user = User.objects.get(id=request.session['user_id'])

        # DoTulink 객체를 생성하거나 기존 객체를 업데이트
        tulink_entry, created = DoTulink.objects.get_or_create(user=user)
        tulink_entry.college = request.POST.get('college')  # 선택된 단과대학
        selected_major = request.POST.get('major')  # 선택된 전공
        tulink_entry.major = selected_major  # 전공 저장
        tulink_entry.save()  # 변경 사항 저장

        # 선택된 전공을 세션에 저장 (다음 단계에서 활용 가능)
        request.session['selected_major'] = selected_major

        # 다음 단계로 리디렉션
        return redirect('webapp:do_tulink2')

    # GET 요청 처리: 사용자에게 선택 가능한 단과대학 및 전공 데이터를 제공
    # UserTulink 객체에서 데이터 가져오기 (기본 데이터를 제공하는 테이블)
    tulink_data = UserTulink.objects.first()
    context = {
        # 단과대학 리스트 (콤마로 구분된 데이터)
        'colleges': tulink_data.college.split(",") if tulink_data and tulink_data.college else [],
        # 전공 리스트 (줄바꿈으로 구분된 데이터)
        'majors': tulink_data.tutoring_major.split("\n") if tulink_data and tulink_data.tutoring_major else [],
    }

    # 선택 화면 렌더링
    return render(request, 'webapp/do_tulink1.html', context)

#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------



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

#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------





# do_tulink3: 가능 시간대 선택
from datetime import datetime  # 현재 날짜와 시간을 가져오기 위한 모듈

def do_tulink3(request):
    """
    가능 시간대 선택 페이지
    - POST 요청: 사용자가 선택한 가능 시간대 데이터를 저장.
    - GET 요청: 오늘 날짜에 해당하는 선택 가능한 시간대를 템플릿에 전달.
    """
    if request.method == 'POST':  # POST 요청 처리
        # 세션에서 현재 로그인된 사용자 ID를 가져오고, User 객체를 조회
        user = User.objects.get(id=request.session['user_id'])

        # DoTulink 객체를 생성하거나 기존 객체를 업데이트
        tulink_entry, created = DoTulink.objects.get_or_create(user=user)

        # 현재 날짜의 요일을 가져와 한글로 변환
        today = datetime.now().strftime("%a")  # 현재 요일 (e.g., 'Mon', 'Tue')
        korean_days = {
            'Mon': '월', 'Tue': '화', 'Wed': '수',
            'Thu': '목', 'Fri': '금', 'Sat': '토', 'Sun': '일'
        }
        today_korean = korean_days.get(today, 'Unknown')  # 오늘 요일의 한글 이름

        # 사용자가 선택한 가능 시간대 리스트 가져오기
        selected_times = request.POST.getlist('available_times')  # 다중 선택 값 리스트로 가져옴

        # 오늘 요일을 첫 번째 시간대 앞에 추가
        if selected_times:
            combined_available_times = [f"{today_korean},{selected_times[0]}"] + selected_times[1:]
        else:
            combined_available_times = []  # 선택된 값이 없으면 빈 리스트

        # 시간대 리스트를 세미콜론(;)으로 연결하여 저장
        tulink_entry.available_times = ";".join(combined_available_times)
        tulink_entry.save()  # 변경 사항 저장

        # 다음 단계로 리디렉션
        return redirect('webapp:choice_tulink')

    # GET 요청 처리: 오늘 날짜에 해당하는 선택 가능한 시간대를 제공
    # UserTulink 데이터 가져오기
    tulink_data = UserTulink.objects.first()
    available_times = []

    # "today:"로 시작하는 줄만 처리
    if tulink_data and tulink_data.available_times:
        for line in tulink_data.available_times.splitlines():
            if line.startswith("today:"):
                # "today:" 접두어 제거하고 시간대만 추출
                available_times = [
                    time.strip() for time in line.replace("today:", "").split(",") if time.strip()
                ]
                break  # 첫 번째 "today:" 줄만 처리

    # 템플릿에 전달할 컨텍스트 데이터
    context = {
        'available_times': available_times,  # 오늘 날짜에 해당하는 선택 가능한 시간대
    }

    # 템플릿 렌더링
    return render(request, 'webapp/do_tulink3.html', context)


#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------

#from django.db.models import Q  # OR 조건 검색을 위한 Q 객체
#from django.shortcuts import render  # 템플릿 렌더링
#from django.http import HttpResponse  # HTTP 응답
#from .models import User, DoTulink  # User와 DoTulink 모델

def choice_tulink(request):
    # 현재 로그인한 사용자 확인
    user_id = request.session.get('user_id')  # 세션에서 사용자 ID 가져오기
    if not user_id:  # 로그인하지 않은 경우 로그인 페이지로 리디렉션
        return redirect('webapp:login_view')

    user = User.objects.get(id=user_id)  # 로그인한 사용자 객체 가져오기

    # 현재 로그인한 사용자의 Dotulink 데이터 가져오기
    try:
        latest_record = DoTulink.objects.get(user=user)  # 로그인한 사용자의 Dotulink 데이터 가져오기
        print("현재 로그인한 사용자의 Dotulink 데이터:", latest_record)  # 디버깅용
    except DoTulink.DoesNotExist:
        print("현재 로그인한 사용자의 Dotulink 데이터가 없습니다.")  # 디버깅용
        return render(request, 'webapp/choice_tulink.html', {'users': [], 'latest_record': None, 'matching_users': []})



#----------------------------------여기까지는 이상없음----------------------------------




    # Major, Sub Major, Available Times를 나누기
    major_parts = latest_record.major.split(';') if latest_record.major else []  # Major 필드를 세미콜론으로 분리
    sub_major_parts = latest_record.sub_major.split(';') if latest_record.sub_major else []  # Sub Major 필드를 세미콜론으로 분리
    time_parts = latest_record.available_times.split(';') if latest_record.available_times else []  # Available Times 필드를 세미콜론으로 분리

    # 저장된 값 확인
    print("전공 스플릿 잘 됐는지 Parts:", major_parts)  # Major 데이터 확인
    print("세부전공 스플릿 잘 됐는지:", sub_major_parts)  # Sub Major 데이터 확인
    print("시간대 스플릿 잘 됐는지:", time_parts)  # Available Times 데이터 확인

    # ----------------------------------여기까지는 이상없음----------------------------------







    # 매칭 로직
    matching_users = User.objects.filter(
        Q(my_tutoring_major__icontains=latest_record.major) |  # User의 my_tutoring_major 필드에서 Major가 포함된 사용자 필터링
        Q(my_tutoring_sub_major__icontains=latest_record.sub_major)  # User의 my_tutoring_sub_major 필드에서 Sub Major가 포함된 사용자 필터링
    ).exclude(id=user.id).distinct()  # 로그인한 사용자 제외


    # 매칭된 유저 출력 (디버깅용)
    print("전공과 세부전공 매칭된 유저 리스트:")
    for user in matching_users:
        print(
            f"ID: {user.id}, Name: {user.name}, Email: {user.email}, Major: {user.my_tutoring_major}, Sub Major: {user.my_tutoring_sub_major}")


    # ----------------------------------여기까지는 이상없음----------------------------------
    # Dotulink 시간대 데이터 분리
    dotulink_times = []
    for time_part in time_parts:
        try:
            dotulink_day, dotulink_hour = time_part.split(',')
            dotulink_times.append((dotulink_day.strip(), dotulink_hour.strip()))
        except ValueError:
            print(f"유효하지 않은 Dotulink 시간 데이터: {time_part}")




    # 날짜 기준으로 사용자 필터링
    date_filtered_users = []  # 날짜로 필터링된 사용자 리스트
    for user in matching_users:  # 전공으로 필터링된 사용자들
        user_day_time_map = {}  # 사용자 시간 데이터를 요일 기준으로 정리
        print(f"현재 확인 중인 유저: {user.name}, 시간대: {user.my_available_times}")  # 현재 유저 정보 출력

        # 사용자 시간 데이터를 줄 단위로 처리
        for user_time_line in user.my_available_times.splitlines():  # 줄 단위로 분리
            try:
                user_day, user_hours = user_time_line.split(',')  # 요일과 시간대를 분리
                user_day = user_day.strip()  # 요일 앞뒤 공백 제거
                user_hours = [hour.strip() for hour in user_hours.split(';')]  # 시간을 세미콜론으로 나눔
                user_day_time_map[user_day] = user_hours  # 요일별 시간대 저장
            except ValueError:
                print(f"유효하지 않은 사용자 시간 데이터: {user_time_line}")  # 형식 오류 데이터 출력
                continue

        print(f"유저 요일+시간 데이터: {user_day_time_map}")  # 사용자 요일+시간 데이터 출력

        # Dotulink 요일과 사용자 요일 비교
        for dotulink_day, _ in dotulink_times:
            print(f"Dotulink 요일: {dotulink_day}, 유저 요일 데이터: {user_day_time_map.keys()}")  # 비교 대상 출력
            if dotulink_day in user_day_time_map:  # 사용자 요일이 Dotulink 요일과 겹치는지 확인
                print(f"매칭된 유저: {user.name}, 매칭 요일: {dotulink_day}")  # 매칭된 유저 정보 출력
                date_filtered_users.append(user)
                break  # 매칭된 사용자는 중복 추가 방지

    # 디버깅: 날짜 기준으로 필터링된 사용자 출력
    print("날짜로 필터링된 사용자:")
    for user in date_filtered_users:
        print(f"{user.name} - {user.my_available_times}")  # 필터링 결과 출력

    ###############################검사중###############################검사중###############################검사중
###############################검사중###############################검사중###############################검사중
###############################검사중###############################검사중###############################검사중
###############################검사중###############################검사중###############################검사중

    # 시간대 기준으로 필터링
    final_users = []  # 최종 매칭된 사용자 리스트
    for user in date_filtered_users:  # 날짜 필터링을 통과한 사용자들
        user_times = []  # 사용자 시간 데이터 (요일,시간)
        print(f"현재 확인 중인 유저: {user.name}, 시간대: {user.my_available_times}")  # 유저 시간대 출력

        # 사용자 시간대를 줄 단위로 처리
        for user_time_line in user.my_available_times.splitlines():  # 줄 단위로 분리
            try:
                user_day, user_hours = user_time_line.split(',')  # 요일과 시간대 분리
                user_day = user_day.strip()  # 요일 앞뒤 공백 제거
                user_hours = [hour.strip() for hour in user_hours.split(';')]  # 시간대를 세미콜론으로 분리
                for hour in user_hours:
                    user_times.append((user_day, hour))  # (요일, 시간) 형태로 저장
            except ValueError:
                print(f"유효하지 않은 사용자 시간 데이터: {user_time_line}")  # 형식 오류 메시지 출력
                continue

        print(f"{user.name}의 유효한 시간 데이터: {user_times}")  # 유저의 유효한 시간 데이터 출력

        # 시간대 비교
        for dotulink_day, dotulink_hour in dotulink_times:  # Dotulink 요청된 요일, 시간 확인
            for user_day, user_hour in user_times:
                if dotulink_day == user_day:  # 요일이 동일한 경우
                    # Dotulink 요청 시간대가 사용자의 시간 범위에 포함되는지 확인
                    if user_hour in dotulink_hour or dotulink_hour in user_hour:
                        if user not in final_users:  # 중복 방지
                            final_users.append(user)  # 매칭된 사용자 추가
                        break  # 매칭된 경우 반복 종료

    # 디버깅용: 최종 매칭된 사용자 출력
    print("최종 매칭된 사용자:")
    for user in final_users:
        print(f"{user.name} - {user.my_available_times}")

    print("매칭된 유저들:")  # 매칭 결과 출력
    for user in final_users:
        print(user)  # 매칭된 사용자 정보를 출력 (디버깅용)

    # 템플릿으로 전달할 컨텍스트 데이터 정의
    context = {
        'users': User.objects.all(),  # 전체 사용자 정보 (필요하다면 필터링 가능)
        'latest_record': latest_record,  # 현재 로그인한 사용자의 Dotulink 데이터
        'matching_users': final_users,  # 매칭된 사용자 리스트
    }
    return render(request, 'webapp/choice_tulink.html', context)  # choice_tulink.html 템플릿 렌더링

#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import User, UserLink, UserUsageCount

@login_required
def reserve_tutor_view(request, user_id):
    """
    선택한 튜터와 현재 로그인한 사용자의 정보를 바탕으로 예약을 처리하는 뷰
    """
    try:
        # 선택한 튜터 정보를 User 모델에서 가져옴
        tutor = User.objects.get(id=user_id)

        # 현재 로그인한 사용자 ID를 세션에서 가져옴
        current_user_id = request.session.get('user_id')
        if not current_user_id:
            return redirect('webapp:login_view')  # 세션에 로그인 정보가 없으면 로그인 페이지로 리디렉션
        current_user = User.objects.get(id=current_user_id)  # 현재 로그인한 사용자 정보

        # HTTP POST 요청 처리 (폼 제출 시)
        if request.method == 'POST':
            # 폼 데이터에서 선택한 시간대와 질문 내용 가져오기
            selected_time_slot = request.POST.get('selected_time_slot')
            question = request.POST.get('question')

            # 시간대와 질문이 비어 있는 경우 에러 반환
            if not selected_time_slot or not question:
                return HttpResponse("시간대 또는 질문이 누락되었습니다.", status=400)

            # 현재 로그인한 사용자의 UserLink와 UserUsageCount 가져오기
            user_link, created = UserLink.objects.get_or_create(user=current_user)  # Link 잔액 정보 가져오기 또는 생성
            user_usage_count, created = UserUsageCount.objects.get_or_create(user=current_user)  # 이용 횟수 정보 가져오기 또는 생성

            # Link 잔액이 부족한 경우
            if user_link.link_balance <= 0:
                return HttpResponse("Link 잔액이 부족합니다.", status=400)

            # Link 잔액 차감 및 이용 횟수 증가
            user_link.link_balance -= 1
            user_link.save()  # 데이터베이스에 저장
            user_usage_count.usage_count += 1
            user_usage_count.save()  # 데이터베이스에 저장

            # 예약자에게 예약 완료 알림 이메일 전송
            send_mail(
                subject='[Tulink] 예약 알림',  # 이메일 제목
                message=(
                    f"-- 안녕하십니까 Tulink를 이용해주셔서 감사합니다 {current_user.name}님 --\n"
                    f"{current_user.name}님의 오늘 예약하신 {tutor.name}님의 정보입니다.\n"
                    f"              <<예약정보>>\n\n"
                    f"{tutor.name}님의 전공: {tutor.my_current_major}\n"
                    f"{tutor.name}님의 세부 전공: {tutor.my_tutoring_sub_major}\n"
                    f"{tutor.name}님과의 예약 시간: {selected_time_slot}\n\n"
                    f"{current_user.name}님의 질문: {question}\n\n"
                    f"예약이 성공적으로 완료되었습니다."
                ),
                from_email='noreply@tulink.com',  # 발신자 이메일
                recipient_list=[current_user.email],  # 예약자 이메일
                fail_silently=False,  # 실패 시 예외 발생
            )

            # 튜터에게 예약 알림 이메일 전송
            send_mail(
                subject='[Tulink] 예약 알림',  # 이메일 제목
                message=(
                    f"-- 안녕하십니까 Tulink를 이용해주셔서 감사합니다 {tutor.name}님 --\n"
                    f"{tutor.name}님의 오늘 예약하신 예약자 {current_user.name}님의 정보입니다.\n"
                    f"              <<예약정보>>\n\n"
                    f"- {current_user.name}님의 전공: {current_user.my_current_major}\n"
                    f"- {current_user.name}님의 세부 전공: {current_user.my_tutoring_sub_major}\n"
                    f"- {current_user.name}님과의 예약 시간: {selected_time_slot}\n\n"
                    f"- {current_user.name}님의 질문: {question}\n\n"
                    f"예약이 성공적으로 완료되었습니다."
                ),
                from_email='noreply@tulink.com',  # 발신자 이메일
                recipient_list=[tutor.email],  # 튜터 이메일
                fail_silently=False,  # 실패 시 예외 발생
            )

            # 예약 완료 후 완료 페이지로 리디렉션
            return redirect('webapp:complete')

        # GET 요청 처리: 현재 날짜를 기준으로 가능한 시간대 필터링
        today = datetime.now().strftime("%a")  # 현재 날짜를 요일로 가져옴 (Mon, Tue 등)
        korean_days = {
            "Mon": "월", "Tue": "화", "Wed": "수", "Thu": "목",
            "Fri": "금", "Sat": "토", "Sun": "일"
        }
        today_korean = korean_days.get(today, "Unknown")  # 한글 요일로 변환

        # 튜터의 가능한 시간대 필터링
        user_available_times = tutor.my_available_times.splitlines()  # 줄 단위로 시간대 분리
        today_time_slots = []  # 오늘 날짜에 해당하는 시간대를 저장할 리스트

        for entry in user_available_times:  # 튜터의 모든 가능한 시간대를 반복
            try:
                day, time_slots = entry.split(",")  # 요일과 시간대를 분리
                if day.strip() == today_korean:  # 오늘의 요일과 일치하는 경우
                    today_time_slots = time_slots.split(";")  # 시간대를 리스트로 저장
            except ValueError:
                continue  # 형식 오류가 있는 경우 생략

        # 템플릿에 전달할 컨텍스트 데이터 정의
        context = {
            'tutor': tutor,  # 선택한 튜터 정보
            'today_time_slots': today_time_slots,  # 오늘의 가능한 시간대
            'current_user': current_user,  # 현재 로그인한 사용자 정보
        }
        return render(request, 'webapp/reserve_tutor.html', context)  # 템플릿 렌더링

    except User.DoesNotExist:
        return HttpResponse("해당 유저를 찾을 수 없습니다.", status=404)  # 튜터 정보를 찾지 못한 경우 404 에러 반환



#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------




def complete_view(request):
    return render(request, 'webapp/complete.html')




# 튜터링 신청 처리 뷰
def tutoring_submit(request, user_id):
    """
    사용자가 선택한 시간과 질문을 바탕으로 튜터링 요청을 처리하는 뷰
    :param request: HTTP 요청 객체
    :param user_id: 튜터의 ID (해당 튜터에게 요청)
    """
    if request.method == 'POST':  # 요청이 POST 방식일 경우 처리
        # User 모델에서 튜터 정보를 가져오기
        user = User.objects.get(id=user_id)  # 요청 대상 튜터 ID를 기준으로 사용자 가져오기

        # HTML 폼에서 전달된 데이터 가져오기
        selected_time = request.POST.get('time')  # 선택한 시간대
        question = request.POST.get('question')  # 사용자가 작성한 질문

        # TutoringRequest 모델에 새로운 요청 생성 및 저장
        TutoringRequest.objects.create(
            tutor=user,  # 요청 대상 튜터 객체
            time=selected_time,  # 선택된 시간대
            question=question  # 사용자가 입력한 질문
        )

        # 요청이 성공적으로 처리되었으면 완료 페이지로 리디렉션
        return redirect('success_page')  # 성공 페이지로 이동

    # POST 방식이 아닌 경우 에러 메시지 반환
    return HttpResponse("Invalid Request")  # 유효하지 않은 요청 메시지




#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------



# 마이페이지 뷰
def mypage_view(request):
    """
    마이페이지: 로그인한 사용자가 입력한 정보들을 확인.
    """
    user_id = request.session.get('user_id')  # 세션에서 사용자 ID 가져오기
    if not user_id:  # 사용자 ID가 없으면 로그인 페이지로 리디렉션
        return redirect('webapp:login_view')

    user = User.objects.get(id=user_id)  # 데이터베이스에서 사용자 객체 가져오기

    # 사용자 Link 잔액 및 메달 정보 가져오기
    usage_count, _ = UserUsageCount.objects.get_or_create(user=user, defaults={"usage_count": 0})
    link_balance, _ = UserLink.objects.get_or_create(user=user, defaults={"link_balance": 5})

    # 메달 이미지 경로 설정
    medal_image = staticfiles_storage.url("road.jpg") if usage_count.usage_count > 49 else staticfiles_storage.url("library.jpg")

    # Link 잔액 텍스트 색상 결정
    link_color = "gold" if usage_count.usage_count > 49 else "silver"

    # 사용자 데이터를 템플릿에 전달
    context = {
        'user_name': user.name,  # 사용자 이름
        'user_email': user.email,  # 사용자 이메일
        'user_major': user.my_current_major,  # 현재 소속 전공
        'user_tutoring_major': user.my_tutoring_major,  # 튜터링할 전공
        'user_available_days': user.my_available_days,  # 가능한 요일
        'user_available_times': user.my_available_times,  # 가능한 시간대
        'link_balance': link_balance.link_balance,  # 사용자 Link 잔액
        'medal_image': medal_image,  # 메달 이미지 경로
        'link_color': link_color,  # Link 잔액 텍스트 색상
    }

    return render(request, 'webapp/mypage.html', context)  # mypage.html 템플릿 렌더링


#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------


@login_required  # 로그인한 사용자만 접근 가능하도록 제한
def delete_account_view(request):
    """
    사용자 계정을 삭제하는 뷰
    """
    # 세션에서 현재 로그인한 사용자 ID 가져오기
    user_id = request.session.get('user_id')
    if not user_id:  # 로그인하지 않은 경우
        return redirect('webapp:login_view')  # 로그인 페이지로 리디렉션

    try:
        # 데이터베이스에서 사용자 객체 가져오기
        user = User.objects.get(id=user_id)

        # 사용자 계정 삭제
        user.delete()

        # 세션 데이터를 삭제하여 로그아웃 처리
        request.session.flush()

        # 계정 삭제 후 로그인 페이지로 리디렉션
        return redirect('webapp:login_view')

    except User.DoesNotExist:
        # 사용자가 존재하지 않는 경우 처리
        return HttpResponse("사용자를 찾을 수 없습니다.", status=404)  # 404 에러 응답 반환





#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------

#뷰는 이상이 없습니다 시발~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


import json


# 회원정보 수정 페이지 뷰
def edit_user_view(request):
    """
    회원정보 수정 페이지
    """

    if request.method == 'POST':
        # 세션에서 user_id 가져오기
        user_id = request.session.get('user_id')  # 로그인된 사용자의 ID를 세션에서 가져옵니다.

        # POST 요청 처리
        if not user_id:  # 만약 세션에 user_id가 없다면, 즉 로그인이 되어 있지 않으면
            return redirect('webapp:mypage_view')  # 로그인 페이지로 리디렉션

        # 로그인된 사용자의 User 객체 가져오기
        user = User.objects.get(id=user_id)

        # 현재 소속 전공 저장
        user.my_current_major = request.POST.get('current_major')

        #까지는 확실함-----------------------------------------------------------------

        # 튜터링 전공 및 세부 전공 저장
        tutoring_majors = request.POST.getlist('tutoring_major[]')  # 사용자가 선택한 튜터링 전공을 리스트로 가져옵니다.
        tutoring_sub_majors = request.POST.getlist('tutoring_sub_major[]')  # 사용자가 선택한 튜터링 세부 전공을 리스트로 가져옵니다.
        user.my_tutoring_major = ";".join(tutoring_majors)
        user.my_tutoring_sub_major = ";".join(tutoring_sub_majors)

        # 사용자가 선택한 튜터링 가능 요일 데이터를 리스트로 가져옵니다.
        available_days = request.POST.getlist('available_days[]')  # 예: ['월', '화']

        # 사용자가 선택한 튜터링 가능 시간대를 저장할 딕셔너리를 초기화합니다.
        available_times = {}

        # POST 요청 데이터에서 시간대 필드를 반복적으로 처리합니다.
        for key, values in request.POST.lists():
            if key.startswith('available_times['):  # 키 이름이 'available_times['로 시작하는지 확인
                index = key.split('[')[1].split(']')[0]  # 예: '0', '1'
                day = available_days[int(index)]  # 예: '월' 또는 '화'
                available_times[day] = values  # 예: {'월': ['10~11', '11~12']}

        # 요일별 시간대 데이터를 하나의 문자열로 변환하여 저장할 준비를 합니다.
        times_result = "\n".join([f"{day},{';'.join(times)}" for day, times in available_times.items()])

        # 사용자 객체의 필드에 선택한 요일 데이터를 저장합니다.
        user.my_available_days = "\n".join(available_days)
        user.my_available_times = times_result
        user.save()  # 변경된 User 객체를 데이터베이스에 저장합니다.

        # --- 출력 확인용 로그 ---
        print("Current Majors:", user.my_current_major)
        print("Tutoring Majors:", user.my_tutoring_major)
        print("Tutoring Sub Majors:", user.my_tutoring_sub_major)
        print("Available Days:", user.my_available_days)
        print("Available Times:", user.my_available_times)

        return redirect('webapp:mypage_view')  # 3단계 페이지로 리디렉션

    # GET 요청 처리
    else:
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('webapp:mypage_view')  # 로그인되지 않은 사용자 리디렉션

        user = User.objects.get(id=user_id)
        tulink_data = UserTulink.objects.first()

        if not tulink_data:
            return render(request, 'webapp/error.html', {'message': 'UserTulink 데이터가 없습니다.'})  # 오류 메시지

        # 전공과 세부 전공을 매칭
        tutoring_data = {}
        major_lines = tulink_data.tutoring_major.split("\n")
        sub_major_lines = tulink_data.tutoring_sub_major.split("\n")

        for major_line, sub_major_line in zip(major_lines, sub_major_lines):
            major_key = major_line.split(",")[0].strip()
            sub_major_values = sub_major_line.split(",")
            tutoring_data[major_key] = [sub.strip() for sub in sub_major_values]

        available_times_by_day = {}
        if tulink_data and tulink_data.available_times:
            for entry in tulink_data.available_times.split("\n"):
                day, times = entry.split(":")
                available_times_by_day[day] = times.split(",")

        # --- 출력 확인용 로그 ---
        print("Tutoring Data:", tutoring_data)
        print("Available Days:", tulink_data.available_days.split(","))
        print("Available Times:", available_times_by_day)

        # 컨텍스트에 데이터를 담아서 템플릿에 전달
        context = {
            'current_majors': tulink_data.current_major.split(","),
            'tutoring_data': tutoring_data,
            'available_days': tulink_data.available_days.split(",") if tulink_data else [],
            'available_times': available_times_by_day,
            'user': user  # 사용자 정보도 전달
        }

        return render(request, 'webapp/edit_user.html', context)  # 템플릿 렌더링



#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------
#---------------------------------------구분선-------------------------------------------



from django.contrib.staticfiles.storage import staticfiles_storage  # 이미지를 불러오는 경로를 설정하기 위해 사용
from django.contrib.staticfiles.storage import staticfiles_storage  # 이미지를 불러오는 경로를 설정하기 위해 사용

def buy_link_view(request):
    """
    Link 구매 페이지를 렌더링하는 뷰 함수.
    사용자 데이터를 가져와 Link 구매 옵션과 관련 정보를 템플릿에 전달합니다.
    """

    # 1. 세션에서 사용자 ID를 가져옴 (로그인 확인)
    user_id = request.session.get('user_id')
    if not user_id:
        # 로그인되지 않은 경우 로그인 페이지로 리디렉션
        return redirect('webapp:login_view')

    # 2. 데이터베이스에서 사용자 정보 가져오기
    user = User.objects.get(id=user_id)

    # 3. 사용자의 이용 횟수와 Link 잔액 정보 가져오기 (없으면 기본값 생성)
    usage_count, _ = UserUsageCount.objects.get_or_create(user=user, defaults={"usage_count": 0})
    link_balance, _ = UserLink.objects.get_or_create(user=user, defaults={"link_balance": 5})

    # 4. 메달 이미지 설정
    medal_image = staticfiles_storage.url("road.jpg") if usage_count.usage_count > 49 else staticfiles_storage.url("library.jpg")

    # 5. Link 잔액 텍스트 색상 결정
    link_color = "gold" if usage_count.usage_count > 49 else "silver"

    # 6. 기본 Link 가격 설정
    link_prices = {
        1: 1900,
        5: 1900 * 5,
        10: 1900 * 10,
        15: 1900 * 15,
        20: 1900 * 20,
    }

    # 7. 할인된 가격 계산
    discounted_prices = {
        5: int(link_prices[5] * (0.92 if usage_count.usage_count > 49 else 0.95)),  # 5 Link 할인율
        10: int(link_prices[10] * (0.88 if usage_count.usage_count > 49 else 0.93)),  # 10 Link 할인율
        15: int(link_prices[15] * (0.84 if usage_count.usage_count > 49 else 0.92)),  # 15 Link 할인율
        20: int(link_prices[20] * (0.80 if usage_count.usage_count > 49 else 0.90)),  # 20 Link 할인율
    }

    # 8. Link 구매 옵션 데이터 조합
    link_options = []
    for count, price in link_prices.items():
        link_options.append({
            "count": count,  # Link 수량
            "price": price,  # 기본 가격
            "discounted_price": discounted_prices.get(count, "없음"),  # 할인 가격 (없으면 '없음')
        })

    # 9. 템플릿에 전달할 컨텍스트 데이터 구성
    context = {
        "user_name": user.name,  # 사용자 이름
        "link_balance": link_balance.link_balance,  # 현재 Link 잔액
        "medal_image": medal_image,  # 메달 이미지 경로
        "link_color": link_color,  # Link 잔액 텍스트 색상
        "link_options": link_options,  # Link 구매 옵션 리스트
    }

    # 10. 템플릿 렌더링 및 반환
    return render(request, 'webapp/buy_link.html', context)  # buy_link.html 템플릿에 데이터 전달








def scan_qr_view(request):
    """
    QR 스캔 페이지
    """

    # URL에서 price 값을 가져옵니다.
    # 사용자가 버튼을 누를 때 전달된 price 값을 가져오기 위해 request.GET.get()을 사용합니다.

    price = request.GET.get('price', '').strip()  # 공백 제거

    # 가격에 따른 이미지 파일 이름을 매핑합니다.
    # 특정 price 값에 해당하는 이미지 파일명을 사전에 정의한 딕셔너리로 저장합니다.
    # 예: "1900" -> "base_1Link.jpeg", "8740" -> "gold_5Link.jpeg" 등.
    image_map = {
        "1900": "base_1Link.jpeg",  # 기본 가격 1900원에 대한 이미지
        "8740": "gold_5Link.jpeg",  # 할인된 골드 5Link에 대한 이미지
        "16720": "gold_10Link.jpeg",  # 할인된 골드 10Link에 대한 이미지
        "23940": "gold_15Link.jpeg",  # 할인된 골드 15Link에 대한 이미지
        "30400": "gold_20Link.jpeg",  # 할인된 골드 20Link에 대한 이미지
        "9025": "BronSil_5Link.jpeg",  # 할인된 은/동 5Link에 대한 이미지
        "17670": "BronSil_10Link.jpeg",  # 할인된 은/동 10Link에 대한 이미지
        "26220": "BronSil_15Link.jpeg",  # 할인된 은/동 15Link에 대한 이미지
        "34200": "BronSil_20Link.jpeg",  # 할인된 은/동 20Link에 대한 이미지
    }

    # 사용자가 선택한 price 값에 해당하는 이미지 파일명을 가져옵니다.
    # price 값이 image_map 딕셔너리에 없을 경우, 기본 이미지 파일 이름("default_image.jpeg")을 사용합니다.
    image_file = image_map.get(price, "default_image.jpeg")

    # static 파일의 경로를 생성합니다.
    # staticfiles_storage.url()을 사용하여 이미지 파일의 전체 경로를 생성합니다.
    image_path = staticfiles_storage.url(image_file)

    # URL에서 가져온 price 값을 로그로 출력합니다.
    print(f"Received price value: {price}")



    # 템플릿으로 전달할 데이터를 딕셔너리에 담습니다.
    # price 값과 이미지 경로(image_path)를 템플릿에서 사용하기 위해 context에 추가합니다.
    context = {
        "price": price,  # 선택된 가격 정보를 템플릿에 전달
        "image_path": image_path,  # 해당 가격에 맞는 이미지 경로를 템플릿에 전달
    }

    # "webapp/scan_qr.html" 템플릿을 렌더링하고 context 데이터를 전달합니다.
    return render(request, "webapp/scan_qr.html", context)


