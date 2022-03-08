import os
import sys

from django.core.management import call_command
from django.utils import timezone

from core.models import (
    Division,
    League,
    Season,
    SubDivision,
    Team,
    TeamStaff,
    TeamStaffType,
    User,
)


def generate_test_fixture_data(write_file=True, verbose=True):
    """
    2 Seasons
        2 Leagues
            2 Divisions
                2 SubDivisions
                    2 Teams

    48 teams total.
    """

    if (
        Season.objects.count() > 2
        or League.objects.count() > 4
        or Division.objects.count() > 8
        or SubDivision.objects.count() > 16
        or Team.objects.count() > 32
        or User.objects.count() > 62
    ):
        print("#### WARNING ####")
        print(
            "Object counts in core tables are greater than test fixture data generation."
        )
        if (
            input(
                "Are you certain you want to clear all data and reset? (y/N):"
            ).lower()
            != "y"
        ):
            sys.exit()

    TeamStaff.objects.all().delete()
    TeamStaffType.objects.all().delete()
    Team.objects.all().delete()
    SubDivision.objects.all().delete()
    Division.objects.all().delete()
    League.objects.all().delete()
    Season.objects.all().delete()
    User.objects.all().delete()

    type_coach, _ = TeamStaffType.objects.get_or_create(name="Coach")
    type_convenor, _ = TeamStaffType.objects.get_or_create(name="Convenor")
    type_vp, _ = TeamStaffType.objects.get_or_create(name="VP")
    type_admin, _ = TeamStaffType.objects.get_or_create(name="Admin")

    current_year = timezone.now().year
    for s in range(current_year, current_year + 2):
        season = Season.objects.create(
            name=f"{s}-{s+1}",
            start=timezone.datetime(s, 9, 1),
            end=timezone.datetime(s + 1, 8, 31),
        )

        admin_user = User.objects.create(email=f"{season} Admin")
        TeamStaff.objects.create(season=season, type=type_admin, user=admin_user)

        if verbose:
            print(season)

        for league in ["HL", "REP"]:
            league = League.objects.create(name=league, season=season)

            if verbose:
                print("\t", league)

            vp_user = User.objects.create(email=f"{season} {league} VP")

            TeamStaff.objects.create(
                type=type_vp,
                season=season,
                league=league,
                user=vp_user,
            )

            subdivision_listing = ["Blue", "White"]
            if league.name == "REP":
                subdivision_listing = ["A", "AA"]

            for division in ["U10", "U11"]:

                division = Division.objects.create(
                    name=division, league=league, season=season
                )

                division_user = User.objects.create(
                    email=f"{season} {league} {division} Division"
                )

                TeamStaff.objects.create(
                    type=type_vp,
                    season=season,
                    league=league,
                    division=division,
                    user=division_user,
                )

                if verbose:
                    print("\t\t", division, division_user)

                for subdivision in subdivision_listing:
                    subdivision = SubDivision.objects.create(
                        name=subdivision,
                        division=division,
                        season=season,
                        league=league,
                    )

                    subdivision_user = User.objects.create(
                        email=f"{season} - {league} - {division} - {subdivision} - SubDivision"
                    )

                    if verbose:
                        print("\t\t\t", subdivision, subdivision_user, sep=" / ")

                    TeamStaff.objects.create(
                        type=type_convenor,
                        season=season,
                        league=league,
                        division=division,
                        subdivision=subdivision,
                        user=subdivision_user,
                    )

                    for team in ["Graham", "Henry"]:
                        team = Team.objects.create(
                            season=season,
                            league=league,
                            division=division,
                            subdivision=subdivision,
                            name=team,
                        )

                        coach_user = User.objects.create(
                            email=f"{season} - {league} - {division} - {subdivision} - {team} - Coach"
                        )

                        TeamStaff.objects.create(
                            type=type_coach,
                            season=season,
                            league=league,
                            division=division,
                            subdivision=subdivision,
                            team=team,
                            user=coach_user,
                        )

                        if verbose:
                            print("\t\t\t\t", team, coach_user, sep=" - ")

        print("Seasons Generated:", Season.objects.count())
        print("Leagues Generated:", League.objects.count())
        print("Divisions Generated:", Division.objects.count())
        print("SubDivisions Generated:", SubDivision.objects.count())
        print("Teams Generated:", Team.objects.count())
        print("Users Generated:", User.objects.count())

    if write_file:
        os.makedirs("core/fixtures/", exist_ok=True)
        with open("core/fixtures/test_fixtures.json", "w") as f:
            call_command("dumpdata", "core", "--indent", "4", stdout=f)
