from django.contrib import admin
from .models import Category,Item,Bid

# Register your models here.
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(Item)
