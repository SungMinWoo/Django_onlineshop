from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

# Create your views here.
from shop.models import Product
from coupon.forms import AddCouponForm
from .forms import AddProductForm
from .cart import Cart


@require_POST
def add(request, product_id):
    # 뒤에 나오는 매개변수는 주소에 내용이 포함되어 넘기는 것
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    # 템플릿을 렌더링하여 이렇게 쓰는 것, api로 짰으면 값만 반환해주면됨

    form = AddProductForm(request.POST)
    # 클라이언트 -> 서버로 데이터를 전달
    # 유효성 검사, injection 전처리
    # form을 통해 내용을 전달하면 기본적인 보안에 괜찮음
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], is_update=cd['is_update'])

    return redirect('cart:detail') # 담았던 안담았던 상세페이지로 보내야함함


def remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:detail')


def detail(request):
    cart = Cart(request)
    add_coupon = AddCouponForm()
    for product in cart:
        product['quantity_form'] = AddProductForm(initial={'quantity':product['quantity'],
                                                           'is_update':True})
    return render(request, 'cart/detail.html', {'cart':cart,
                                                'add_coupon':add_coupon})
