from django.db import models
from django.contrib.auth.models import User
import uuid


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, null=True)
    email = models.EmailField(null=True)
    image = models.ImageField(upload_to='images/customers/', null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    @property
    def get_personal_data(self):
        try:
            personal_data = self.personaldata
        except:
            personal_data = None
        return personal_data


class Composer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, null=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    email = models.EmailField(null=True)
    rating = models.FloatField(blank=True, null=True)
    image = models.ImageField(upload_to='images/composers/', null=True, blank=True)
    balance = models.FloatField(default=0, blank=True, null=True)

    def __str__(self):
        return self.user.username

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Genre(models.Model):
    name = models.CharField(max_length=200, null=True)
    image = models.ImageField(upload_to='images/genres/', null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Instrument(models.Model):
    name = models.CharField(max_length=200, null=True)
    image = models.ImageField(upload_to='images/instruments/', null=True, blank=True)
    font_path = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Emotion(models.Model):
    name = models.CharField(max_length=200, null=True)
    image = models.ImageField(upload_to='images/emotions/', null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    composer = models.ForeignKey(Composer, on_delete=models.SET_NULL, blank=True, null=True)
    image = models.ImageField(upload_to='images/products/', null=True, blank=True)
    file = models.FileField(upload_to='files/', max_length=200, null=True)
    duration = models.DurationField(null=True)
    standard_price = models.DecimalField(max_digits=7, decimal_places=2)
    premium_price = models.DecimalField(max_digits=7, decimal_places=2)

    genres = models.ManyToManyField(Genre, blank=True)
    instruments = models.ManyToManyField(Instrument, blank=True)
    emotions = models.ManyToManyField(Emotion, blank=True)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(max_length=200, null=True)
    project = models.CharField(max_length=200, null=True)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        order_items = self.orderitem_set.all()
        return sum([item.get_price for item in order_items])

    @property
    def get_cart_count(self):
        order_items = self.orderitem_set.all()
        return order_items.count()


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    premium = models.BooleanField(max_length=200, null=True)
    licence_file = models.FileField(upload_to='files/', max_length=200, null=True)

    def __str__(self):
        return self.product.name

    @property
    def get_price(self):
        if self.premium:
            return self.product.premium_price
        else:
            return self.product.standard_price


class PersonalData(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    index = models.CharField(max_length=200, null=True)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=20, null=True)
    country = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.customer.user.username


class ComposerOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, null=True)
    premium = models.BooleanField(max_length=200, null=True)
    composer = models.ForeignKey(Composer, on_delete=models.SET_NULL, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    description = models.CharField(max_length=500, null=True)
    file = models.FileField(upload_to='files/', max_length=200, null=True)
    license_file = models.FileField(upload_to='files/', max_length=200, null=True)
    price = models.FloatField()
    confirm = models.BooleanField(max_length=200, null=True)
    customer_confirm = models.BooleanField(max_length=200, null=True)
    finish = models.BooleanField(max_length=200, null=True)
    accept = models.BooleanField(max_length=200, null=True)
    project = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class FreelanceOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=500, null=True)
    premium = models.BooleanField(max_length=200, null=True)
    price = models.FloatField()
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class Bet(models.Model):
    freelance_order = models.ForeignKey(FreelanceOrder, on_delete=models.SET_NULL, blank=True, null=True)
    composer = models.ForeignKey(Composer, on_delete=models.SET_NULL, blank=True, null=True)
    price = models.FloatField()
    text = models.CharField(max_length=500, null=True)

    def __str__(self):
        return str(self.composer.user.id)


class Feedback(models.Model):
    composer = models.ForeignKey(Composer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.OneToOneField(ComposerOrder, on_delete=models.SET_NULL, null=True)
    mark = models.FloatField()
    text = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.mark)


class AiOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, blank=True, null=True)
    is_premium = models.BooleanField(max_length=200, null=True)
    accepted = models.BooleanField(max_length=200, default=False)
    completed = models.BooleanField(max_length=200, default=False)
    file = models.FileField(upload_to='files/', max_length=200, null=True)
    audio_file = models.FileField(upload_to='files/', max_length=200, null=True)
    license_file = models.FileField(upload_to='files/', max_length=200, null=True)
    price = models.FloatField(default=5)
    project = models.CharField(max_length=200, null=True)

