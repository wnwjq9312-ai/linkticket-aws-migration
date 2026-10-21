from django.contrib.auth.models import AbstractUser
from django.db import models

class Member(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="휴대폰 번호")
    birth_date = models.DateField(blank=True, null=True, verbose_name="생년월일")
    gender = models.CharField(max_length=10, blank=True, null=True, verbose_name="성별")
    marketing_agree = models.BooleanField(default=False, verbose_name="마케팅 수신 동의")