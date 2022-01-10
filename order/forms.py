# 장고에서 폼을 쓰는 이유는 사용자(클라이언트)들이 어떤 정보를 서버로 보낼 때
# 조금더 정제된 모습으로 하기위해서
# 사용자로부터 넘어온 데이터를 그대로 받아오면 안되기 때문에 유효성 검사를 진행
from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order # Order에 관한 내용이 다 나옴
        fields = ['first_name','last_name','email','address',
                  'postal_code','city']
        # '__all__'로 하면 모든 필드가 나오는 것이고 위에 방식은 따로 원하는 것만 입력 받으려고함
        # 이 폼은 ordercreate에서 사용하는 폼임
