from django.contrib import admin

from .models import Player
from .models import Score

admin.site.register(Player)
admin.site.register(Score)
