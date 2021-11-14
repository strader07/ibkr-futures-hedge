from django.contrib import admin
from main.models import *


# Register your models here.
@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'is_active', 'symbol', 'num_contract',
        'tick', 'long_dpp', 'long_dpp_up', 'long_dpp_dn','short_dpp',
        'short_dpp_up', 'short_dpp_dn', 'created_at', 'updated_at'
    )
