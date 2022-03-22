from django.shortcuts import render

from team.helpers import add_selected_team


@add_selected_team
def index(request, team):

    return render(request, "team/index.html", {"team": team})
