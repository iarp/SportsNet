from django.test import TestCase

from core.models import Division, League, PermissionOverrides, Season, SubDivision, User
from core.perms import add_override_permission
from core.test_helpers import FixtureBasedTestCase

from .models import Staff, StaffStatus, StaffType, Team, TeamStatus, TeamStatusReason


class StaffAccessTests(FixtureBasedTestCase):
    def test_staff_str_equals_user_username(self):
        ts = Staff.objects.first()
        self.assertEqual(str(ts.user), str(ts))

    def test_season_staff_returns_one_entry(self):
        season1 = Season.objects.first()
        self.assertEqual(1, season1.staff.count())

    def test_seasonal_admins_can_edit_teams(self):
        season1 = Season.objects.first()
        season2 = Season.objects.exclude(pk=season1.pk).first()
        user1_admin = Staff.objects.get(type__name="Admin", season=season1)
        user2_admin = Staff.objects.get(type__name="Admin", season=season2)

        team1 = season1.teams.first()
        team2 = season2.teams.first()

        self.assertIs(True, team1.can_edit(user1_admin))
        self.assertIs(False, team2.can_edit(user1_admin))

        self.assertIs(False, team1.can_edit(user2_admin))
        self.assertIs(True, team2.can_edit(user2_admin))

    def test_team_method_can_edit_accepts_user_or_staff_objects(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        self.assertIs(True, team1.can_edit(team1_coach))
        self.assertIs(True, team1.can_edit(team1_coach.user))

    def test_coach_cannot_edit_others_teams(self):
        team1 = Team.objects.first()
        team2 = Team.objects.last()

        team2_coach = team2.staff.first()

        self.assertIs(False, team1.can_edit(team2_coach))

    def test_coach_can_edit_own_team(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        self.assertIs(True, team1.can_edit(team1_coach))

    def test_convenor_can_edit_own_divisions_teams(self):
        team1 = Team.objects.first()
        team2 = team1.subdivision.teams.first()

        team1_convenor = Staff.objects.filter(
            type__name="Convenor",
            season=team1.season,
            league=team1.league,
            division=team1.division,
            subdivision=team1.subdivision,
            team__isnull=True,
        ).first()

        self.assertIs(True, team1.can_edit(team1_convenor))
        self.assertIs(True, team2.can_edit(team1_convenor))

    def test_convenor_cannot_edit_other_divisions_teams(self):
        team1 = Team.objects.first()
        team2 = team1.subdivision.teams.first()

        team1_convenor = (
            Staff.objects.filter(
                type__name="Convenor",
                season=team1.season,
                league=team1.league,
                division=team1.division,
                team__isnull=True,
            )
            .exclude(subdivision=team1.subdivision)
            .first()
        )

        self.assertIs(False, team2.can_edit(team1_convenor))

    def test_coach_cannot_vote(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        self.assertIs(False, team1.can_vote(team1_coach))

    def test_coach_only_has_one_permissible_team(self):
        team1 = Team.objects.first()
        team1_coach = team1.staff.first()

        i = 0
        for team in Team.objects.all():
            i += team.can_edit(team1_coach)

        self.assertEqual(1, i)

    def test_convenor_can_edit_own_subdivison_teams(self):
        team1 = Team.objects.first()
        team1_convenor = team1.subdivision.staff.first()

        for team in team1.subdivision.teams.all():
            self.assertIs(True, team.can_edit(team1_convenor))

    def test_convenor_only_has_two_permissible_teams(self):
        team1 = Team.objects.first()
        team1_convenor = team1.subdivision.staff.first()

        i = 0
        for team in Team.objects.all():
            i += team.can_edit(team1_convenor)

        self.assertEqual(2, i)

    def test_vp_can_edit_own_league_teams(self):
        team1 = Team.objects.first()
        team1_vp = team1.league.staff.first()

        for team in team1.league.teams.all():
            self.assertIs(True, team.can_edit(team1_vp))

    def test_vp_only_has_league_permissible_teams(self):
        team1 = Team.objects.first()
        team1_vp = team1.league.staff.first()

        for team in team1.league.teams.all():
            self.assertIs(True, team.can_edit(team1_vp))

        i = 0
        for team in Team.objects.all():
            i += team.can_edit(team1_vp)

        self.assertEqual(team1.league.teams.count(), i)


class StaffAccessExtraPermissionsTests(FixtureBasedTestCase):
    def test_coach1_with_extra_permissions_stafftype_can_edit_team2(self):
        team1 = Team.objects.first()
        team2 = Team.objects.exclude(pk=team1.pk).first()
        team3 = Team.objects.exclude(pk__in=[team1.pk, team2.pk]).first()

        coach1 = team1.staff.first()
        coach2 = team2.staff.first()

        self.assertNotEqual(coach1, coach2)

        self.assertIs(True, team1.can_edit(coach1))
        self.assertIs(False, team2.can_edit(coach1))
        self.assertIs(False, team3.can_edit(coach1))

        self.assertIs(False, team1.can_edit(coach2))
        self.assertIs(True, team2.can_edit(coach2))
        self.assertIs(False, team3.can_edit(coach2))

        add_override_permission(coach1, team2, "team_can_edit", True)

        self.assertEqual(1, PermissionOverrides.objects.count())

        self.assertIs(True, team1.can_edit(coach1))
        self.assertIs(True, team2.can_edit(coach1))
        self.assertIs(False, team3.can_edit(coach1))

        self.assertIs(False, team1.can_edit(coach2))
        self.assertIs(True, team2.can_edit(coach2))
        self.assertIs(False, team3.can_edit(coach2))

    def test_coach_can_vote_when_voting_enabled(self):
        team1 = Team.objects.first()
        team2 = team1.division.teams.exclude(pk=team1.pk).first()

        self.assertEqual(team1.division, team2.division)
        self.assertNotEqual(team1, team2)

        team1_coach = team1.staff.first()
        team2_coach = team2.staff.first()

        self.assertEqual(team1_coach.type.pk, team2_coach.type.pk)

        self.assertIs(False, team1.can_vote(team1_coach))
        self.assertIs(False, team1.can_vote(team2_coach))
        self.assertIs(False, team2.can_vote(team1_coach))
        self.assertIs(False, team2.can_vote(team2_coach))

        StaffType.objects.filter(name="Coach").update(team_can_vote=True)

        self.assertIs(True, team1.can_vote(team1_coach))
        self.assertIs(True, team2.can_vote(team2_coach))

        self.assertIs(False, team1.can_vote(team2_coach))
        self.assertIs(False, team2.can_vote(team1_coach))

    def test_coach_can_vote_on_another_team_with_extra_permissions(self):
        team1 = Team.objects.first()
        team2 = Team.objects.last()

        team1_coach = team1.staff.first()

        team1_coach.permissions_add_override(team1, "team_can_vote", True)

        self.assertIs(True, team1.can_vote(team1_coach))
        self.assertIs(False, team2.can_vote(team1_coach))

    def test_coach_can_vote_with_subdivision_permissions(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        team1_coach.permissions_add_override(team1.subdivision, "team_can_vote", True)

        for team in team1.subdivision.teams.all():
            self.assertIs(True, team.can_vote(team1_coach))

    def test_coach_can_vote_with_division_permissions(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        team1_coach.permissions_add_override(team1.division, "team_can_vote", True)

        for team in team1.division.teams.all():
            self.assertIs(True, team.can_vote(team1_coach))

    def test_coach_can_vote_with_league_permissions(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        team1_coach.permissions_add_override(team1.league, "team_can_vote", True)

        for team in team1.league.teams.all():
            self.assertIs(True, team.can_vote(team1_coach))

    def test_coach_can_vote_with_season_permissions(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        team1_coach.permissions_add_override(team1.season, "team_can_vote", True)

        for team in team1.season.teams.all():
            self.assertIs(True, team.can_vote(team1_coach))


class TeamSignalsTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username="user")
        self.season = Season.objects.create(name="Season 1")
        self.league = League.objects.create(season=self.season, name="League 1")
        self.division = Division.objects.create(
            league=self.league, season=self.season, name="Division 1"
        )
        self.subdivision = SubDivision.objects.create(
            league=self.league,
            division=self.division,
            season=self.season,
            name="SubDivision 1",
        )

        team_status_approved = TeamStatus.objects.create(name="APPROVED")
        team_status_reason = TeamStatusReason.objects.create(
            name="N/A", status=team_status_approved
        )

        self.team = Team.objects.create(
            season=self.season,
            league=self.league,
            division=self.division,
            subdivision=self.subdivision,
            name="Team 1",
            status=team_status_approved,
            status_reason=team_status_reason,
        )
        self.stafftype = StaffType.objects.create(name="staff type")
        self.staffstatus = StaffStatus.objects.create(name="staff status")

        return super().setUp()

    def create_staff(self, *args, **kwargs):
        return Staff.objects.create(
            user=self.user,
            type=self.stafftype,
            status=self.staffstatus,
            *args,
            **kwargs,
        )

    def test_ensure_staff_entry_has_proper_ids_with_season_object(self):
        obj = self.create_staff(season=self.season)
        self.assertEqual(self.season.pk, obj.season_id)
        self.assertIsNone(obj.league_id)
        self.assertIsNone(obj.division_id)
        self.assertIsNone(obj.subdivision_id)
        self.assertIsNone(obj.team_id)

    def test_ensure_staff_entry_has_proper_ids_with_league_object(self):
        obj = self.create_staff(league=self.league)

        self.assertEqual(self.season.pk, obj.season_id)
        self.assertEqual(self.league.pk, obj.league_id)
        self.assertIsNone(obj.division_id)
        self.assertIsNone(obj.subdivision_id)
        self.assertIsNone(obj.team_id)

    def test_ensure_staff_entry_has_proper_ids_with_division_object(self):
        obj = self.create_staff(division=self.division)

        self.assertEqual(self.season.pk, obj.season_id)
        self.assertEqual(self.league.pk, obj.league_id)
        self.assertEqual(self.division.pk, obj.division_id)
        self.assertIsNone(obj.subdivision_id)
        self.assertIsNone(obj.team_id)

    def test_ensure_staff_entry_has_proper_ids_with_subdivision_object(self):
        obj = self.create_staff(subdivision=self.subdivision)

        self.assertEqual(self.season.pk, obj.season_id)
        self.assertEqual(self.league.pk, obj.league_id)
        self.assertEqual(self.division.pk, obj.division_id)
        self.assertEqual(self.subdivision.pk, obj.subdivision_id)
        self.assertIsNone(obj.team_id)

    def test_ensure_staff_entry_has_proper_ids_with_team_object(self):
        obj = self.create_staff(team=self.team)

        self.assertEqual(self.season.pk, obj.season_id)
        self.assertEqual(self.league.pk, obj.league_id)
        self.assertEqual(self.division.pk, obj.division_id)
        self.assertEqual(self.subdivision.pk, obj.subdivision_id)
        self.assertEqual(self.team.pk, obj.team_id)