from lib2to3.fixes.fix_input import context

from django.shortcuts import render


# Create your views here.

from django.http import HttpResponseRedirect #5장 DB게시판 읽기
from django.shortcuts import render,redirect,get_object_or_404 #5장 DB게시판 읽기(redirect)
import pandas as pd #5장 DB게시판 읽기
from .forms import PostForm #5장 DB게시판 읽기
from .models import Bible, Board,Rhema #4장 DB, 5장 DB게시판 읽기,6장 게시판 수정삭제
from django.utils import timezone #5장 DB게시판 읽기
from .forms import WriteForm #6장 게시판 수정삭제

from django.contrib.auth import authenticate,login  #8장
from django.contrib.auth.decorators import login_required #8장

import logging #7장
logger=logging.getLogger('webapp') #7장

from .forms import UserForm #8장 핵심!!!!!


def index(request):
    context = {'message': '아 나이스 11월 4일 오지환.'}
    return render(request, 'webapp/index.html', context)

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

 #3장템플릿 시스템
def grid(request, type):

    items = ['원주역에 내린다', '30번을 탄다', '연세대학교에 내린다','창조관으로 온다', '창271호로 올라온다']
    context = {'type':type, 'process' : items}

    return render(request, 'webapp/grid.html', context)


#4장 DB
def bible(request):
    bible_text = Bible.objects.order_by('verse_no')
    context = {'bible_text' : bible_text}

    return render(request,'webapp/bible.html',context)


#5장 DB게시판 읽기
def post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.created = timezone.now()
            post.updated = timezone.now()
            post.save()

            return redirect('/webapp/board')
    else:
        form = PostForm()

        context = {'form': form}

        return  render(request, 'webapp/post.html',context)

#5장 DB게시판 읽기
def board(request):
    # Board 모델의 모든 객체를 id 순으로 정렬하여 가져옴
    querySet = Board.objects.all().order_by('id')

    # 필요한 필드만 선택하여 딕셔너리 형태로 반환
    q = querySet.values('id', 'subject', 'artical', 'created', 'updated')

    # Pandas DataFrame으로 변환
    df_board = pd.DataFrame.from_records(q)

    # DataFrame 데이터를 리스트 형태로 변환
    l_data = []
    for i, data in df_board.iterrows():
        l_data.append(data.values.tolist())

    # 템플릿에 전달할 context 정의
    context = {'articles': l_data}

    # 템플릿 렌더링
    return render(request, 'webapp/board.html', context)



#6장 게시판 수정삭제
def bible(request):
    bible_text = Bible.objects.all().order_by('verse_no')
    context = {'bible_text': bible_text}
    return render(request, 'webapp/bible.html', context)


#6장 게시판 수정삭제
def rhema_read(request, id):
    bible = get_object_or_404(Bible, id=id)
    rhema = Rhema.objects.filter(bible_id=id)


    context = {'bible': bible, 'rhema': rhema}
    return render(request, 'webapp/read.html', context)



#6장 게시판 수정삭제
def rhema_write(request, id):
    if request.method == "POST":
        form = WriteForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.bible_id = id
            post.created = timezone.now()
            post.updated = timezone.now()
            post.save()
            return redirect('/webapp/rhema/read/' + str(id))
    else:
        form = WriteForm()

    context = {'form': form}
    return render(request, 'webapp/write.html', context)



#6장 게시판 수정삭제
def rhema_update(request, id):
    record = get_object_or_404(Rhema, id=id)
    if request.method == "POST":
        form = WriteForm(request.POST, instance=record)
        if form.is_valid():
            post = form.save(commit=False)
            post.rhema = form.cleaned_data['rhema']
            post.updated = timezone.now()
            post.save()
            return redirect('/webapp/bible')
    else:
        form = WriteForm(instance=record)

    context = {'form': form}
    return render(request, 'webapp/write.html', context)

#6장 게시판 수정삭제
def rhema_delete(request, id):
    # rhema=get_object_or_404(Rhema,pk=id) #6장
    # rhema.delete() #6장
    # return redirect('/webapp/bible') #6장


#7장 레마 딜리트
    try:
        rhema = get_object_or_404(Rhema,pk=id)
    except Exception as e:

        logger.error(f'An error occured:{e}',exc_info=False)

        context={'err_msg':'404'}
        return render(request,'webapp/error.html',context)
    else:
        rhema.delete()
        return redirect('/webapp/bible')




#8장
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/webapp/bible')
    else:
        form = UserForm()
    return render(request, 'webapp/signup.html', {'form': form})


#8장
@login_required(login_url='webapp:login')
def rhema_delete(request, id):
    try:
        rhema = get_object_or_404(Rhema, pk=id)
    except Exception as e:
        logger.error(f'An error occurred: {e}', exc_info=False)
        context = {'err_msg': '404'}
        return render(request, 'webapp/error.html', context)
    else:
        rhema.delete()
        return redirect('/webapp/bible')


