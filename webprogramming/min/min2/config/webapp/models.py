from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import User

# Create your models here.


#4장 DB모델
class Bible(models.Model):
    book_name = models.CharField(max_length=20)
    book_no   = models.IntegerField(blank=True, null=True)
    chap_no   = models.IntegerField(blank=True, null=True)
    verse_no  = models.IntegerField(blank=True, null=True)
    book_text = models.TextField()

#5장 DB게시판 읽기
class Board(models.Model):
    subject   = models.CharField(max_length=20)
    artical   = models.TextField()
    created   = models.DateTimeField()
    updated   = models.DateTimeField()

#6장 DB게시판 수정
class Rhema(models.Model):
    bible = models.ForeignKey(Bible, on_delete=models.CASCADE)
    rhema = models.TextField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
