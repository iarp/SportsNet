from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Division, League, Season, SubDivision, User


@admin.register(Season, League, Division, SubDivision)
class GeneralAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
