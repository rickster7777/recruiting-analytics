from django.contrib import admin
from .models import City, State, Address, School
# Register your models here.

admin.site.register(City)
admin.site.register(State)
admin.site.register(Address)
admin.site.register(School)
