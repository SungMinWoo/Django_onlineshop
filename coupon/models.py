from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# 나중에 회원가입 폼도 이 라이브러리를 사용
# Create your models here.


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True) # 겹치면 할인율을 정하기 힘드니 유니크
    use_from = models.DateTimeField()
    use_to = models.DateTimeField() # 사용 기간
    amount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100000)])
    # 최대 최소 제약조건 10만원까지 할인되는 것
    active = models.BooleanField()

    def __str__(self):
        return self.code
