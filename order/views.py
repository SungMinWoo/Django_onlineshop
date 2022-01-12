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
                #order.discount = cart.coupon.amount # 이렇게 작성해도됨
                order.discount = cart.get_discount_total() # 얘가 더 안전하고 정확한 로직
                order.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
            cart.clear() # 주분이 들어갔으면 카트를 비움
            return render(request, 'order/created.html', {'order':order})
    else: # 여기는 get 방식
        form = OrderCreateForm() # 여기에 입력 받음
    # 사용자 입력을 잘못 받았을 때 오류를 반환하고 끝내지 않고 내려오게만들려고 return을 밖으로
    return render(request, 'order/create.html', {'cart':cart, 'form':form})
# JS가 동작하지 않는 환경에서도 주문은 가능해야한다.


def order_complete(request): # 자바스크립트를 사용할 시
    order_id = request.GET.get('order_id') # 시큐어 코딩 어떤 정보가 올지 모르니 한번 걸러주는 것 지금은 안씀
    # order = Order.objects.get(id=order_id)
    order = get_object_or_404(Order, id=order_id) # order가 있으면 밑으로 내려가고 없으면 404로 감
    return render(request, 'order/create.html', {'order':order})


# 에이작스
from django.views.generic.base import View # class형으로 만들때 하는 기본적인 view
from django.http import JsonResponse


class OrderCreateAjaxView(View): # 화면이 변환없이 자바스크립트로 변환이 될때 자바스크립트를 사용하지 않으면 위에 order가 실행됨
    def post(self, request, *args, **kwargs): # post나 get이나 if로 할필요없이 post로 준비해두면된다.
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated":False}, status=403)

        cart = Cart(request)
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False) # 괄호안에 commit=False를 넣으면 쿼리가 날아가진않음
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.amount
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()
            data = {
                "order_id": order.id
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)


class OrderImpAjaxView(View): # 후처리
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated":False}, status=403)

        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        merchant_id = request.POST.get('merchant_id')
        imp_id = request.POST.get('imp_id')
        amount = request.POST.get('amount')

        try:
            trans = OrderTransaction.objects.get(
                order=order,
                merchant_order_id=merchant_id,
                amount=amount
            )
        except:
            trans = None

        if trans is not None:
            trans.transaction_id = imp_id
            trans.success = True
            trans.save()
            order.paid = True
            order.save()

            data = {
                "works": True
            }

            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)