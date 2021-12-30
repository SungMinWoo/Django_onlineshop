from django.db import models
from django.urls import reverse
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    meta_description = models.TextField(blank=True)
    # 검색엔진에 이용되는 정보
    slug = models.SlugField(max_length=200, db_index=True, unique=True, allow_unicode=True)
    # 번호 말고 카테고리 제품으로 접근, db_index 가 true면 pk로 사용함, unique 이름이 유니크함, allow을 사용해야 한글 사용가능
    class Meta:
        ordering = ['name']
        verbose_name = 'category' # 카테고리 단수형 이름
        verbose_name_plural = 'categories' # 복수형 이름 기록

    def __str__(self):
        return self.name
    # 카테고리를 출력하면 나타낼 이름

    def get_absolute_url(self):
        return reverse('shop:product_in_category', args=[self.slug])
    # 상세페이지, 모델을 출력만해도 이부분을 출력하게되어 주소가 자동으로됨


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    # FK라 카테고리가 지워지면 어떻게할지 설정해야하는데 제품은 없어지지않게 SET_NULL로함
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True, allow_unicode=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # 한국은 int로 해도 되지만 외국은 소수점도 있어서 decimal로 만들어줌
    stock = models.PositiveIntegerField()
    available_display = models.BooleanField('Display', default=True)
    available_order = models.BooleanField('Order', default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta: # 다양한 정보를 품고 있다는 뜻, 검색 옵션이나, 정렬옵션
        ordering = ['-created', '-updated']
        index_together = [['id', 'slug']]
        # 두개를 기준으로 잡아주는 필드

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])
