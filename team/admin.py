from django.contrib import admin

from .models import (
    Staff,
    StaffStatus,
    StaffStatusReason,
    StaffType,
    Team,
    TeamNote,
    TeamStatus,
    TeamStatusLog,
)

admin.site.register(
    (
        Staff,
        StaffStatus,
        StaffStatusReason,
        StaffType,
        Team,
        TeamNote,
        TeamStatus,
        TeamStatusLog,
    )
)
