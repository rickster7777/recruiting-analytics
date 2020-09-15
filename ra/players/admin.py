from django.contrib import admin

from .models import (Classification, Comments, FbsOffers, FbsSchools, Notes,
                     OldPlayMakingValues, Player, PlayerType, Positions,
                     SavedSearch)

# Register your models here.
admin.site.register(Player)
admin.site.register(PlayerType)
admin.site.register(Classification)
admin.site.register(Notes)
admin.site.register(Positions)
admin.site.register(FbsOffers)
admin.site.register(SavedSearch)
admin.site.register(Comments)
admin.site.register(FbsSchools)
admin.site.register(OldPlayMakingValues)