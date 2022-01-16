from django.contrib import admin
from .models import OrderItem, Order


import csv
import datetime
from django.http import HttpResponse


def export_to_csv(modeladmin, request, queryset):
    # modeladmin = 어느 애들을 선택해서 가져오는가
    # quertset = 어떤 애들이 선택되어 오는가
    opts = modeladmin.model._meta
    # 필드 정보 얻어오기
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename={}.csv'.format(opts.verbose_name)

    writer = csv.writer(response)
    # response 부분은 파일이 들어와야하는데 response는 결국 파일임
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # csv 파일 컬럼 타이틀 줄
    writer.writerow([field.verbose_name for field in fields])
    # 괄호 않은 필드, csv 헤더 작성해주는 것
    # 실제 데이터 출력
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime): #
                value = value.strftime("%Y-%m-%d")
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = 'Export to CSV' # admin 페이지에 노출될 이름


from django.urls import reverse
# 주소 생성
from django.utils.safestring import mark_safe
# 관리자 페이지에 html 노출이 보안 때문에 안되게 되어있음 하지만 mark_safe로 감싸서 넣어주면 안전한 내용으로 인식


def order_detail(obj):
    return mark_safe('<a href="{}">Detail</a>'.format(reverse('orders:admin_order_detail', args=[obj.id])))
    #

order_detail.short_description = 'Detail'


def order_pdf(obj):
    return mark_safe('<a href="{}">PDF</a>'.format(reverse('orders:admin_order_pdf', args=[obj.id])))

order_pdf.short_description = 'PDF'


class OrderItemInline(admin.TabularInline):
    # TabularInline = 테이블 형태로 보여주겠다
    model = OrderItem
    raw_id_fields = ['product'] # raw_id_fields = 검색 버튼을 가지고 검색할 수 있음


class OrderAdmin(admin.ModelAdmin):
    # list_display = ['id','first_name','last_name','email','address','postal_code','city','paid' , order_detail, order_pdf,'created','updated']
    list_display = ['id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city',
                    'paid', order_detail, 'created', 'updated']
    # 어떤 내용을 목록에 보여줄지
    list_filter = ['paid','created','updated']
    # 필터에 어떤 기준을 집어 넣을지
    inlines = [OrderItemInline] # 다른 모델과 연결되어있는 경우 한페이지 표시하고 싶을 때
    # inlines = 다른 모델의 정보(FK)로 연결되어 있는 정보 같이 등록해주는 것
    actions = [export_to_csv]
    # actions = 주문 목록에 선택한 것을 csv로 뽑아주는 것

admin.site.register(Order, OrderAdmin)