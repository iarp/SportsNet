from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect


def permissable_teams(user, season=None):
    from core.models import Season
    from team.models import Staff

    if isinstance(user, Staff):
        user = user.user

    if season is None:
        season = Season.get_current()

    def get_staff_teams(staff):
        teams = set()
        qs = None
        if staff.team_id:
            teams.add(staff.team)
        elif staff.subdivision_id:
            qs = staff.subdivision.teams.all()
        elif staff.division_id:
            qs = staff.division.teams.all()
        elif staff.league_id:
            qs = staff.league.teams.all()
        else:
            qs = staff.season.teams.all()

        if qs:
            for team in qs:
                teams.add(team)
        return teams

    users_teams = set()

    for staff in user.staff_assignments.filter(season=season):
        users_teams.update(get_staff_teams(staff))

    for staff in user.overridden_permissions.all():
        users_teams.update(get_staff_teams(staff))

    return users_teams


def add_selected_team(func):
    @wraps(func)
    @login_required
    def decorator(request, *args, **kwargs):
        from team.models import Team

        request.session["selected_team_id"] = 2
        selected = request.session.get("selected_team_id")
        if not selected:
            # TODO: Redirect to team selection page
            messages.error(request, "No team selected")
            return redirect("core:index")
        team = get_object_or_404(Team, pk=selected)
        if not team.can_access(request.user):
            # TODO: Redirect to team selection page
            messages.error(request, "Denied access to team")
            return redirect("core:index")
        return func(request, team=team, *args, **kwargs)

    return decorator
