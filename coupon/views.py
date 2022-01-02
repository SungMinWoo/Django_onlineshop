from django.shortcuts import render

from django.shortcuts import redirect
# 장바구니 페이지로 리다이랙트해서 필요
from django.utils import timezone
# 사용 기간 평가, 서버에 남긴 국가의 시간으로 판단
from django.views.decorators.http import require_POST

from .models import Coupon
from .forms import AddCouponForm


@require_POST
def add_coupon(request):
    now = timezone.now()
    form = AddCouponForm(request.Post)
    if form.is_valid():
        code = form.cleaned_data['code']

        try:
            coupon = Coupon.objects.get(code__iexact=code, use_from__lte=now, use_to__gte=now,
                                        active=True)
            # iexact 대소문자 가리지 않고 일치해야하는 것
            # use from lte 와 use to gte사이에 현재 시간이라면
            # active 사용이 가능한 애만 가져온다.
            request.session['coupon_id'] = coupon.id # 나중에 계산할때 집어넣는것
        except Coupon.DoesNotExist: # 장고에서 알아서 발생 시켜줌
            request.session['coupon_id'] = None

    return redirect('cart:detail')
