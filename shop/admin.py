from django.contrib import admin
from .models import *
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    prepopulated_fields = {'slug':['name']}
    # 제품을 등록할때 자동으로 어떤걸 넣어줄지 결정, 자바스크립트가 알아서 동작 튜플 형식으로 사용


admin.site.register(Category, CategoryAdmin)
# 카테고리 모델을 관리자 페이지에 등록 보여지는 목록을 2번째 파라미터로 넣어줌

@admin.register(Product) # 어노테이션 기법, 장고에서는 데코레이터 기법 아래를 부르기전에 실행하는 단계
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'category', 'price', 'stock', 'available_display',
                    'available_order', 'created', 'updated']
    list_filter = ['available_display', 'created', 'updated', 'category']
    prepopulated_fields = {'slug':('name',)}
    # 관리자 페이지에서 Name을 쓰면 slug 부분이 자동으로 채워짐
    list_editable = ['price', 'stock', 'available_display', 'available_order']
    # 목록에서 자주 바꾸는건 여기서 바꾸겠다는 이야기
