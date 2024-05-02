from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Comment)
admin.site.register(Action)
admin.site.register(Achievement)

