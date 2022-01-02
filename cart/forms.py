from django import forms
# 클라이언트 화면에 입력 폽을 만들어주려고 만듦
# 클라이언트가 입력한 데이터에 대한 전처리


class AddProductForm (forms.Form):
    quantity = forms.IntegerField()
    is_update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
    # boolean필드를 사용할때는 꼭 required가 False로 해야함 False일때 가끔 값이 없다고 반환해줄때가 있음
