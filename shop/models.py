
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

def comment_directory_path(instance, filename):
    return 'photo/{0}/{1}'.format(instance.product.id, filename)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderproducts = self.orderproduct_set.all()
        total = sum([product.get_total for product in orderproducts])
        return total

    @property
    def get_cart_total_quantity(self):
        orderproducts = self.orderproduct_set.all()
        total = sum([product.quantity for product in orderproducts])
        return total

    @property
    def get_products(self):
        orderproducts = self.orderproduct_set.all()
        result = [item.product for item in orderproducts]
        return result

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.CharField(max_length=1000, null=True)
    image = models.ImageField(null=True, blank=True)
    image2 = models.ImageField(null=True, blank=True)
    image3 = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    body = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(null=False, blank=False, upload_to=comment_directory_path)

    @property
    def get_count_comments(self):
        comments = self.comment_set.all()
        count = len(comments)
        return count

    def file_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url


class Achievement(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

class Action(models.Model):
    count_comments_all = models.IntegerField(default=0)
    count_comments_view_all = models.IntegerField(default=0)
    count_comments_view = models.IntegerField(default=0)

    count_details_view = models.IntegerField(default=0)
    count_log_in = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)