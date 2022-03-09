from django.contrib import admin

from .models import Staff, StaffStatus, StaffStatusReason, StaffType, Team


@admin.register(Staff, StaffStatus, StaffStatusReason, StaffType, Team)
class GeneralAdmin(admin.ModelAdmin):
    pass
