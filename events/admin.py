from django.contrib import admin

from events.models import Association, Exhibition, Rink, Tournament

# from daterange_filter.filter import DateRangeFilter


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "full_name",
        "location",
        "website",
        "exhibition_is_in_ohf",
        "inserted",
    ]
    ordering = ["weight"]


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    # list_filter = ['association', 'verified', 'source', ('start_date', DateRangeFilter)]
    list_filter = ["association", "verified", "source"]
    list_display = (
        "association",
        "sanction_number",
        "name",
        "location",
        "start_date",
        "verified",
        "inserted_by",
        "permits_count",
    )
    search_fields = ["sanction_number", "start_date", "divisions"]
    ordering = [
        "verified",
        "start_date",
    ]

    raw_id_fields = ["inserted_by"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "association",
                    "name",
                    "sanction_number",
                    "location",
                    ("start_date", "end_date"),
                )
            },
        ),
        ("Optional Data", {"fields": ("divisions",)}),
        (
            "Advanced options",
            {
                "fields": (
                    "source",
                    "verified",
                    "verified_date",
                    "inserted_by",
                    "website",
                    "notes",
                )
            },
        ),
    )

    def permits_count(self, obj):
        return obj.travelpermit_set.count()

    permits_count.short_description = "Permits"


@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = [
        "other_team",
        "other_team_association",
        "destination",
        "arena",
        "start_date",
    ]

    raw_id_fields = ["inserted_by"]


@admin.register(Rink)
class RinkAdmin(admin.ModelAdmin):
    pass
