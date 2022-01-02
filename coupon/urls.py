from django.urls import path

from .views import add_coupon

app_name = 'coupon'

urlpatterns = [
    path('add/', add_coupon, name='add'),
    # 다른 url의 add랑 겹쳐도 app_name의 coupon으로 구분되어 신경쓰지 않아도 된다.
]