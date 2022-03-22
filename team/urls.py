from django.urls import path

from .views import team

app_name = "team"
urlpatterns = [
    path("", team.index, name="index"),
    # path("staff/", staff.staff, name="staff"),
    # path("staff/<int:person_id>/", staff.staff_detail, name="staff_detail"),
    # path('players/', players.players_list, name='players'),
    # path('players/ajax/', players.players_ajax, name='players-ajax'),
    # path('players/<int:player_id>/', players.player_detail, name='player-detail'),
]
