from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from coupon.models import Coupon

from shop.models import Product

class Order(models.Model): # 필드랑 데이터베이스의 실제 타입이 다를 수도 있음
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True) # 오더 정보가 업데이트 될 때
    paid = models.BooleanField(default=False, blank=True)
    # blank가 False가 아닌 경우에 boolean 값을 못전달 받을 수도 있음 소스코드 상으로 하여 없어도는 되지만 직접 추가해야할 경우는 필요

    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name='order_coupon',
                               null=True, blank=True)
    discount = models.IntegerField(default=0,
                                   validators=[MinValueValidator(0), MaxValueValidator(100000)])

    class Meta:
        ordering = ['-created'] # 최신순으로 정렬

    def __str__(self): # 객체 정보를 어떤 정보를 출력할지
        return f'Order {self.id}'

    def get_total_product(self): # 전체 제품의 가격이 같은지 비교
        return sum(item.get_item_price() for item in self.items.all())

    def get_total_price(self):
        total_product = self.get_total_product()
        return total_product - self.discount # 위에 있는 discount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # 제품 참조는 Order, 주문이 지워지면 싹 다 날아가야해서 cascade, related_name은 위에있는 items인데 OrderItem의 order을 축약하여 쓴 것
    # Order 입장에서 쓰는 이름이 related_name
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_products')
    # 제품이 하나라도 주문이 됐으면 삭제 못하게 PROTECT를 거는 것
    price = models.DecimalField(max_digits=10, decimal_places=2) # product에 있는 price필드
    quantity = models.PositiveIntegerField(default=1) # 최소 주문 정보

    def __str__(self):
        return str(self.id) # f문법 써도됨 f'{self.id}'

    def get_item_price(self):
        return self.price * self.quantity
