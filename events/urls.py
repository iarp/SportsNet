from django.urls import path

from events import views

app_name = "events"
urlpatterns = [
    path(
        "tournaments/",
        views.event_list,
        {"event_type": "tournament"},
        name="tournaments-list",
    ),
    path(
        "tournaments/new/",
        views.event_new,
        {"event_type": "tournament"},
        name="tournament-new",
    ),
    path(
        "tournaments/<int:event_id>/",
        views.event_details,
        {"event_type": "tournament"},
        name="tournament-details",
    ),
    path(
        "tournaments/<int:event_id>/verified/",
        views.tournament_verification,
        name="tournament-verify",
    ),
    path(
        "tournaments/<int:event_id>/edit/",
        views.tournament_edit,
        name="tournament-edit",
    ),
    path(
        "exhibitions/",
        views.event_list,
        {"event_type": "exhibition"},
        name="exhibitions-list",
    ),
    path(
        "exhibitions/new/",
        views.event_new,
        {"event_type": "exhibition"},
        name="exhibition-new",
    ),
    path(
        "exhibitions/<int:event_id>/",
        views.event_details,
        {"event_type": "exhibition"},
        name="exhibition-details",
    ),
    path(
        "exhibitions/<int:event_id>/edit/",
        views.exhibition_edit,
        name="exhibition-edit",
    ),
    path(
        "admin/tournaments-needing-verifications/",
        views.tournaments_needing_verification,
        name="tournament-needs-verification",
    ),
]
