from django.contrib import admin
from .models import User, UserSubscription, MyBoard, WatchList
# Register your models here.

admin.site.register(User)
admin.site.register(UserSubscription)
admin.site.register(MyBoard)
admin.site.register(WatchList)
