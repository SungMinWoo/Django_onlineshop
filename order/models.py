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


import hashlib
from .iamport import payments_prepare, find_transaction


class OrderTransactionManager(models.Manager):
    def create_new(self, order, amount, success=None, transaction_status=None):
        if not order:
            raise ValueError("주문 정보 오류")
        order_hash = hashlib.sha1(str(order.id).encode('utf-8')).hexdigest()
        # hashlib에 sha1 암호화 방식임 꼭 이것일 필요는 없음, sha1으로 암호화 하고 hexdigest 방식으로 암호화
        email_hash = str(order.email).split("@")[0]
        final_hash = hashlib.sha1((order_hash + email_hash).encode('utf-8')).hexdigest()[:10]
        # 유니크한 주문번호를 생성하기 위해서 복잡한 형식으로 사용한 것
        # 다른 방법으로는 샵 이름이랑 이메일이랑 번호만 붙여서 보내도됨
        merchant_order_id = str(final_hash)  # 동영상 강의에서 변경

        payments_prepare(merchant_order_id, amount)
        # 결제 준비해달라고 전송

        transaction = self.model( # 여기서 model의 정의를 ordertransaction에서 정의하게 됨
            order=order,
            merchant_order_id=merchant_order_id,
            amount=amount
        )

        if success is not None: # 결제 테스트
            transaction.success = success
            transaction.transaction_status = transaction_status

        try:
            transaction.save()
        except Exception as e:
            print("save error", e)

        return transaction.merchant_order_id


    def get_transaction(self, merchant_order_id):
        # object.뒷부분 추가하는 것
        result = find_transaction(merchant_order_id)
        if result['status'] == 'paid': # 조회한 트렌젝션 정보가 paid라면
            return result
        else:
            return None


class OrderTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    merchant_order_id = models.CharField(max_length=120, null=True, blank=True)
    transaction_id = models.CharField(max_length=120, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # 국내는 소수점이 없어서 필요없긴함
    transaction_status = models.CharField(max_length=220, null=True, blank=True)
    # 결제 대행사에서 결제 양식(길이)가 정해져 있어서 그거에 맞추면됨
    type = models.CharField(max_length=120, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    # success = models.BooleanField(default=False)
    objects = OrderTransactionManager()

    def __str__(self): # 출력했을때 나오는 문자열
        return str(self.order.id)

    class Meta:
        ordering = ['-created']


def order_payment_validation(sender, instance, created, *args, **kwargs):
    # 모델이 세이브가 되어 instance가 생성되었다.
    if instance.transaction_id: # 트렌젝션 id가 있나 확인
        iamport_transaction = OrderTransaction.objects.get_transaction(merchant_order_id=instance.merchant_order_id)
        merchant_order_id = iamport_transaction['merchant_order_id']
        imp_id = iamport_transaction['imp_id']
        amount = iamport_transaction['amount']

        local_transaction = OrderTransaction.objects.filter(merchant_order_id=merchant_order_id, transaction_id=imp_id, amount=amount).exists()
        # 실제 트렌젝션을 가져와서 가격 비교
        if not iamport_transaction or not local_transaction:
            raise ValueError("비정상 거래입니다.")


from django.db.models.signals import post_save
# 모델의 어떤일
post_save.connect(order_payment_validation, sender=OrderTransaction)
# sender orderTransaction 일 때만 시그널을 발생 시킨다. sender이 없으면 모든 모델의 세이브 작업에서 발생시킨다.
