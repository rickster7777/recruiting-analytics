from django.contrib import admin
from .models import ProspectsPersonality, ProspectsNeeds, ProspectsValues, PersonalityInsights
# Register your models here.

admin.site.register(PersonalityInsights)
admin.site.register(ProspectsPersonality)
admin.site.register(ProspectsValues)
admin.site.register(ProspectsNeeds)
