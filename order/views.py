from django.shortcuts import render, get_object_or_404
from .models import *
from cart.cart import Cart
from .forms import *
# Create your views here.


def order_create(request): # request = 요청 정보
    cart = Cart(request)
    # 주소가 똑같은데 뭘로 구분하는가하면 post, get 메소드로 구분을 함
    if request.method == 'POST':
        # get 방식으로 입력했을 때 create는 주문자 정보를 받는 페이지임
        # 같은 페이지에서 POST와 GET을 같이 처리하는데 이유는 다른 페이지에서 처리하면 리소스 낭비
        # 입력받은 정보를 후처리
        form = OrderCreateForm(request.POST)
        # 입력받은 폼을 가지고 validation(필드 확인)해서 쓰려고 request에 post 데이터를 넣어줌
        if form.is_valid(): # 입력 받은 값이 맞다면
            order = form.save()
            if cart.coupon:
                order.coupon = cart.coupon
                #order.discount = cart.coupon.amount
                order.discount = cart.get_discount_total()
                order.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
            cart.clear() # 주분이 들어갔으면 카트를 비움
            return render(request, 'order/created.html', {'order':order})
    else: # 여기는 get 방식
        form = OrderCreateForm() # 여기에 입력 받음
    # 사용자 입력을 잘못 받았을 때 오류를 반환하고 끝내지 않고 내려오게만들려고 return을 밖으로
    return render(request, 'order/create.html', {'cart':cart, 'form':form})
