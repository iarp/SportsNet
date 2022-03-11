from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Division, League, PermissionOverrides, Season, SubDivision, User


admin.site.register((Season, League, Division, SubDivision, PermissionOverrides))
admin.site.register(User, UserAdmin)
