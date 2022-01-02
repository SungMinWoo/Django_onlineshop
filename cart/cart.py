from decimal import Decimal
# 한국에서만 작업하면 굳이 필요없음
from django.conf import settings

from shop.models import Product
from coupon.models import Coupon


class Cart(object):
    def __init__(self, request):
        # 초기화 작업
        self.session = request.session # 장고에서 사용한 request
        cart = self.session.get(settings.CART_ID) # 기존에 카드 정보를 가져오는 것
        if not cart:
            cart = self.session[settings.CART_ID] = {}
        self.cart = cart
        self.coupon_id = self.session.get('coupon_id')

    def __len__(self):
        # iterater 같은 걸 쓸때 몇개가 들어있는지 알 수 있는 것
        return sum(item['quantity'] for item in self.cart.values())
        # 장바구니에 몇개의 상품이 있는지 항상 계산하는게 아닌 len 메소드만 호출하면 되도록하는 것

    def __iter__(self):
        # for문 같은 것 사용시 어떤 요소를 건네줄지
        product_ids = self.cart.keys()

        products = Product.objects.filter(id__in=product_ids)
        # filter는 쿼리문에서 where에 해당함 id라고 하면 id만 달라는 것 id__in은 id가 product_ids에 해당하는 것을 반환

        for product in products:
            self.cart[str(product.id)]['product'] = product
            # 세션에 키 값은 글자로 만들어서 넣음

        for item in self.cart.values(): # 장바구니에 이미 들어 있는 애들
            item['price'] = Decimal(item['price']) # 제품 가격을 숫자형으로 바꿔서 넣어줌
            item['total_price'] = item['price'] * item['quantity'] # 제품 개수와 가격의 합산

            yield item # for문을 돌렸을 때 던져줌 for 문 중간중간 yield를 만나면 밖으로 값을 던져줌

    def add(self, product, quantity=1, is_update=False):
        # 제품을 장바구니에 넣는 것 quantity는 기본값 is_update는 장바구니에서는 update할 필요없다. 상세페이지에서는 추가하면 제품이 추가되니까 True인 듯
        product_id = str(product.id) # 세션에 글자형태로 넣기 위해 str
        if product_id not in self.cart: # 제품 아이디를 읽지 않으면
            self.cart[product_id] = {'quantity':0, 'price':str(product.price)}
            # 제품 정보 집어 넣는 것
            # 제품 정보가 없을때는 담은 것
        if is_update: # 업데이트일 경우에
            self.cart[product_id]['quantity'] = quantity # 제품 정보 수정
        else:
            self.cart[product_id]['quantity'] += quantity # 업데이트가 아니면 변경

        self.save() # 업데이트 정보 저장

    def save(self):
        self.session[settings.CART_ID] = self.cart # 세션에 업데이트 정보 저장
        self.session.modified = True # 제품 정보가 변경 됐을 때

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del(self.cart[product_id])
            self.save()

    def clear(self):
        self.session[settings.CART_ID] = {} # 아래 줄 있어서 save를 따로 해주지않음
        self.session['coupon_id'] = None
        self.session.modified = True

    def get_product_total(self):
        return sum(Decimal(item['price'])*item['quantity'] for item in self.cart.values())

    @property
    # property 어노테이션을 사용
    def coupon(self):
        if self.coupon_id:
            return Coupon.objects.get(id=self.coupon_id)
        return None

    def get_discount_total(self):
        if self.coupon: # 위에 property 때문에 coupon이라는 것을 변수처럼 쓸 수 있다.
            if self.get_product_total() >= self.coupon.amount:
                return self.coupon.amount
        return Decimal(0)

    def get_total_price(self):
        return self.get_product_total() - self.get_discount_total()
