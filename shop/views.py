from django.shortcuts import render, get_object_or_404
# get_object_or_404 특정 오브젝트가 없으면 404로 넘어감
# Create your views here.

from .models import *


def product_in_category(request, category_slug=None):
    # category_slug 부분은 url 설계할 때 어떤 값을 받아서 이 뷰랑 연결할껀지
    current_category = None
    categories = Category.objects.all() # object는 메니저 이름
    products = Product.objects.filter(available_display=True) # 제품을 보여줄 수 있는 애들만 보여주기
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)
        # django는 지연평가를 한다. filter을 몇 번 먹이던 위에서 실행이 이루어져야 아래가 실행이 되기 때문에 상관없다.
    return render(request, 'shop/list.html', {
        'current_category':current_category,
        'categories':categories,
        'products':products,
    })

def product_detail(request, id, product_slug=None):
    product = get_object_or_404(Product, id=id, slug=product_slug)
    return render(request, 'shop/detail.html', {'product':product})