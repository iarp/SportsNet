from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from core.models import (
    Division,
    Gender,
    League,
    Member,
    MemberStatus,
    PermissionOverrides,
    Season,
    SubDivision,
    User,
)
from core.perms import add_override_permission
from core.test_helpers import FixtureBasedTestCase

from . import helpers
from .models import (
    Player,
    PlayerPosition,
    PlayerStatus,
    PlayerStatusLog,
    PlayerType,
    Staff,
    StaffStatus,
    StaffType,
    Team,
    TeamStatus,
    TeamStatusLog,
    TeamStatusReason,
)


class StaffAccessTests(FixtureBasedTestCase):
    def test_staff_str_equals_user_username(self):
        ts = Staff.objects.first()
        self.assertEqual(str(ts.user), str(ts))

    def test_seasonal_admins_can_edit_teams(self):
        season1 = Season.objects.first()
        season2 = Season.objects.exclude(pk=season1.pk).first()
        user1_admin = season1.staff.own().first()
        user2_admin = season2.staff.own().first()

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

    def test_convenor_cannot_edit_other_divisions_teams(self):
        team1 = Team.objects.first()
        team2 = team1.subdivision.teams.first()

        convenor = (
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

        self.assertIs(False, team2.can_edit(convenor))

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
        team1_convenor = team1.subdivision.staff.own().first()

        for team in team1.subdivision.teams.all():
            self.assertIs(True, team.can_edit(team1_convenor))

    def test_convenor_only_has_two_permissible_teams(self):
        team1 = Team.objects.first()
        team1_convenor = team1.subdivision.staff.own().first()

        i = 0
        for team in Team.objects.all():
            i += team.can_edit(team1_convenor)

        self.assertEqual(2, i)

    def test_vp_can_edit_own_league_teams(self):
        team1 = Team.objects.first()
        team1_vp = team1.league.staff.own().first()

        for team in team1.league.teams.all():
            self.assertIs(True, team.can_edit(team1_vp))

    def test_vp_only_has_league_permissible_teams(self):
        team1 = Team.objects.first()
        team1_vp = team1.league.staff.own().first()

        for team in team1.league.teams.all():
            self.assertIs(True, team.can_edit(team1_vp))

        i = 0
        for team in Team.objects.all():
            i += team.can_edit(team1_vp)

        self.assertEqual(team1.league.teams.count(), i)

    def test_division_can_vote_with_division_permissions(self):
        division = Division.objects.first()

        division_staff = division.staff.own().first()

        for team in division.teams.all():
            self.assertIs(True, team.can_edit(division_staff))

    def test_coach_can_access_own_team(self):
        team1 = Team.objects.first()
        team2 = Team.objects.exclude(pk=team1.pk).last()

        team1_coach = team1.staff.first()

        self.assertIs(True, team1.can_access(team1_coach))
        self.assertIs(False, team2.can_access(team1_coach))

    def test_helper_permissiable_teams_for_coach(self):
        season = Season.get_current()
        team1 = Team.objects.filter(season=season).first()

        allowed_teams = helpers.permissable_teams(team1.staff.first())

        self.assertEqual(1, len(allowed_teams))
        self.assertIn(team1, allowed_teams)

    def test_helper_permissiable_teams_for_convenor(self):
        season = Season.get_current()
        team1 = Team.objects.filter(season=season).first()

        convenor = team1.subdivision.staff.first()

        allowed_teams = helpers.permissable_teams(convenor)

        self.assertEqual(team1.subdivision.teams.count(), len(allowed_teams))
        for team in team1.subdivision.teams.all():
            self.assertIn(team, allowed_teams)

    def test_helper_permissiable_teams_for_senior_convenor(self):
        season = Season.get_current()
        team1 = Team.objects.filter(season=season).first()

        number_of_teams = team1.division.teams.count()

        senior_convenor = team1.division.staff.first()

        allowed_teams = helpers.permissable_teams(senior_convenor)

        self.assertEqual(number_of_teams, len(allowed_teams))

        for team in team1.division.teams.all():
            self.assertIn(team, allowed_teams)

    def test_helper_permissiable_teams_for_vp(self):
        season = Season.get_current()
        team1 = Team.objects.filter(season=season).first()

        number_of_teams = team1.league.teams.count()

        vp = team1.league.staff.first()

        allowed_teams = helpers.permissable_teams(vp)

        self.assertEqual(number_of_teams, len(allowed_teams))

        for team in team1.league.teams.all():
            self.assertIn(team, allowed_teams)

    def test_helper_permissiable_teams_for_admin(self):
        season = Season.get_current()
        team1 = Team.objects.filter(season=season).first()

        number_of_teams = team1.season.teams.count()

        admin = team1.season.staff.first()

        allowed_teams = helpers.permissable_teams(admin)

        self.assertEqual(number_of_teams, len(allowed_teams))

        for team in team1.season.teams.all():
            self.assertIn(team, allowed_teams)

    def test_helper_permissiable_teams_for_coach_with_extra_permissions_assigned(self):
        season = Season.get_current()
        team1 = Team.objects.filter(season=season).first()

        team2 = Team.objects.filter(season=season).exclude(pk=team1.pk).last()
        coach2 = team2.staff.first()

        allowed_teams = helpers.permissable_teams(coach2)
        self.assertEqual(1, len(allowed_teams))
        self.assertIn(team2, allowed_teams)

        coach2.permissions_add_override(team1, "team_can_access", True)

        allowed_teams = helpers.permissable_teams(coach2)
        self.assertEqual(2, len(allowed_teams))
        self.assertIn(team1, allowed_teams)
        self.assertIn(team2, allowed_teams)


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

        self.team_status_approved = TeamStatus.objects.create(name="APPROVED")
        self.team_status_clear_flag_true = TeamStatus.objects.create(
            name="CLEAR FLAG", clear_changed_staff_players_flag=True
        )

        self.team_status_approved_reason = self.team_status_approved.reasons.create(
            name="APPROVED", default=True
        )
        self.team_status_clear_flag_true_reason = (
            self.team_status_clear_flag_true.reasons.create(
                name="APPROVED", default=True
            )
        )

        self.team = Team.objects.create(
            season=self.season,
            league=self.league,
            division=self.division,
            subdivision=self.subdivision,
            name="Team 1",
            status=self.team_status_approved,
            status_reason=self.team_status_approved_reason,
        )
        self.stafftype = StaffType.objects.create(name="staff type")
        self.staffstatus = StaffStatus.objects.create(name="staff status")

        return super().setUp()

    def create_staff(self, *args, **kwargs):
        user = User.objects.create_user("test@domain.com", "12345")

        member = Member.objects.create(
            first_name=user.username,
            last_name="Hockey",
            address1="123 Fake Street",
            city="Toronto",
            province="Ontario",
            postal_code="1S34R6",
            date_of_birth=timezone.make_aware(
                timezone.datetime(2012, 1, 15, 0, 0, 0),
                timezone.get_current_timezone(),
            ).date(),
            email=user.email,
            gender=Gender.objects.create(name="test"),
            status=MemberStatus.objects.create(name="test"),
        )

        return Staff.objects.create(
            user=self.user,
            type=self.stafftype,
            status=self.staffstatus,
            member=member,
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

    def test_teamstatuslog_entry_is_create(self):
        team_status = TeamStatus.objects.create(name="REJECTED")
        team_status_reason = TeamStatusReason.objects.create(
            name="REJECTED", status=team_status
        )

        self.assertEqual(0, TeamStatusLog.objects.count())

        self.team.status = team_status
        self.team.status_reason = team_status_reason
        self.team.save()

        self.assertEqual(1, TeamStatusLog.objects.count())

        log = TeamStatusLog.objects.first()

        self.assertEqual(self.team_status_approved, log.old_status)
        self.assertEqual(self.team_status_approved_reason, log.old_status_reason)
        self.assertEqual(team_status, log.new_status)
        self.assertEqual(team_status_reason, log.new_status_reason)

    def test_team_staff_changed_flag_gets_cleared_on_status_change(self):
        self.assertIs(False, self.team.staff_has_changed_flag)

        self.team.staff_has_changed_flag = True
        self.team.save()

        self.assertIs(True, self.team.staff_has_changed_flag)

        self.team.status = self.team_status_clear_flag_true
        self.team.save()

        self.assertIs(False, self.team.staff_has_changed_flag)

    def test_team_players_changed_flag_gets_cleared_on_status_change(self):
        self.assertIs(False, self.team.players_has_changed_flag)

        self.team.players_has_changed_flag = True
        self.team.save()

        self.assertIs(True, self.team.players_has_changed_flag)

        self.team.status = self.team_status_clear_flag_true
        self.team.save()

        self.assertIs(False, self.team.players_has_changed_flag)

    def test_team_staff_and_players_changed_flag_gets_cleared_on_status_change(self):
        self.assertIs(False, self.team.players_has_changed_flag)
        self.assertIs(False, self.team.staff_has_changed_flag)

        self.team.players_has_changed_flag = True
        self.team.staff_has_changed_flag = True
        self.team.save()

        self.assertIs(True, self.team.players_has_changed_flag)
        self.assertIs(True, self.team.staff_has_changed_flag)

        self.team.status = self.team_status_clear_flag_true
        self.team.save()

        self.assertIs(False, self.team.players_has_changed_flag)
        self.assertIs(False, self.team.staff_has_changed_flag)

    def test_staff_creation_updates_team_staff_changed_flag_status(self):

        self.assertIs(False, self.team.staff_has_changed_flag)

        self.create_staff(team=self.team)

        self.assertIs(True, self.team.staff_has_changed_flag)

    def test_staff_changes_updates_team_staff_changed_flag_status(self):

        self.assertIs(False, self.team.staff_has_changed_flag)

        self.create_staff(team=self.team)

        self.team.staff_has_changed_flag = False
        self.team.save()

        staff = self.team.staff.first()
        staff.first_name = "test"
        staff.save()

        self.assertIs(True, self.team.staff_has_changed_flag)

        self.team.staff_has_changed_flag = False
        self.team.save()

        self.assertIs(False, self.team.staff_has_changed_flag)

    def test_staff_changes_does_not_update_team_staff_changed_flag_status_with_stafftype_flag_disabled(
        self,
    ):

        self.assertIs(False, self.team.staff_has_changed_flag)

        self.stafftype.change_causes_staff_flag_on_team_to_enable = False
        self.stafftype.save()

        self.create_staff(team=self.team)

        self.assertIs(False, self.team.staff_has_changed_flag)

        staff = self.team.staff.first()
        staff.first_name = "test"
        staff.save()

        self.assertIs(False, self.team.staff_has_changed_flag)

    def test_change_team_status_reason_set_to_none_if_reason_is_not_assigned(self):
        self.team.status = TeamStatus.objects.create(name="new status")
        self.team.save()

        self.assertIsNone(self.team.status_reason)

    def test_change_team_status_reason_does_not_change_if_reason_is_assigned(self):
        new_status = TeamStatus.objects.create(name="new status")
        new_status_reason = new_status.reasons.create(name="new status reason")

        self.assertEqual(self.team.status_reason, self.team_status_approved_reason)

        self.team.status = new_status
        self.team.status_reason = new_status_reason
        self.team.save()

        self.assertEqual(self.team.status_reason, new_status_reason)

    def test_new_team_with_status_gets_default_statusreason(self):

        status = TeamStatus.objects.create(name="test")
        reason = status.reasons.create(name="test", default=True)

        team = Team.objects.create(
            season=self.season,
            league=self.league,
            division=self.division,
            subdivision=self.subdivision,
            name="Team 2",
            status=status,
        )

        self.assertEqual(reason, team.status_reason)

    def test_new_team_with_status_without_default_reason_stays_none(self):

        status = TeamStatus.objects.create(name="test")

        team = Team.objects.create(
            season=self.season,
            league=self.league,
            division=self.division,
            subdivision=self.subdivision,
            name="Team 2",
            status=status,
        )

        self.assertIsNone(team.status_reason)


class StaffManagerTests(FixtureBasedTestCase):
    def test_staff_objects_head_coach_raises_on_all_but_team_model(self):
        team = Team.objects.first()
        self.assertIsInstance(team.staff.head_coach(), Staff)
        self.assertRaisesMessage(
            TypeError,
            "head_coach is available on the Team instance.",
            League.objects.first().staff.head_coach,
        )
        self.assertRaisesMessage(
            TypeError,
            "head_coach is available on the Team instance.",
            Division.objects.first().staff.head_coach,
        )
        self.assertRaisesMessage(
            TypeError,
            "head_coach is available on the Team instance.",
            SubDivision.objects.first().staff.head_coach,
        )

    def test_season_staff_returns_all_staff_entries(self):
        season = Season.objects.first()
        self.assertEqual(
            Staff.objects.filter(season=season).count(),
            season.staff.count(),
        )

    def test_season_staff_filter_type_coach_returns_correct_number(self):
        season = Season.objects.first()
        self.assertEqual(16, season.staff.filter(type__name="Coach").count())

    def test_league_staff_returns_all_staff_entries(self):
        season = Season.objects.first()
        league = season.leagues.first()
        self.assertEqual(
            Staff.objects.filter(season=season, league=league).count(),
            league.staff.count(),
        )

    def test_division_staff_returns_all_staff_entries(self):
        season = Season.objects.first()
        league = season.leagues.first()
        division = league.divisions.first()
        self.assertEqual(
            Staff.objects.filter(
                season=season, league=league, division=division
            ).count(),
            division.staff.count(),
        )

    def test_subdivision_staff_returns_all_staff_entries(self):
        season = Season.objects.first()
        league = season.leagues.first()
        division = league.divisions.first()
        subdivision = division.subdivisions.first()
        self.assertEqual(
            Staff.objects.filter(
                season=season, league=league, division=division, subdivision=subdivision
            ).count(),
            subdivision.staff.count(),
        )

    def test_team_staff_returns_all_staff_entries(self):
        season = Season.objects.first()
        league = season.leagues.first()
        division = league.divisions.first()
        subdivision = division.subdivisions.first()
        team = subdivision.teams.first()

        self.assertEqual(
            Staff.objects.filter(
                season=season,
                league=league,
                division=division,
                subdivision=subdivision,
                team=team,
            ).count(),
            team.staff.count(),
        )

    def test_season_staff_vps_returns_correct_number(self):
        self.assertEqual(2, Season.objects.first().staff.vps().count())

    def test_incorrect_model_staff_vps_raises_typeerror(self):
        error = "vps is available on the Season instance."
        self.assertRaisesMessage(TypeError, error, League.objects.first().staff.vps)
        self.assertRaisesMessage(TypeError, error, Division.objects.first().staff.vps)
        self.assertRaisesMessage(
            TypeError, error, SubDivision.objects.first().staff.vps
        )
        self.assertRaisesMessage(TypeError, error, Team.objects.first().staff.vps)

    def test_staff_senior_convenors_returns_correct_number(self):
        self.assertEqual(4, Season.objects.first().staff.senior_convenors().count())
        self.assertEqual(2, League.objects.first().staff.senior_convenors().count())

    def test_incorrect_model_staff_senior_convenors_raises_typeerror(self):
        self.assertRaisesMessage(
            TypeError,
            "senior_convenors is available on the Season or League instance.",
            Division.objects.first().staff.senior_convenors,
        )
        self.assertRaisesMessage(
            TypeError,
            "senior_convenors is available on the Season or League instance.",
            SubDivision.objects.first().staff.senior_convenors,
        )
        self.assertRaisesMessage(
            TypeError,
            "senior_convenors is available on the Season or League instance.",
            Team.objects.first().staff.senior_convenors,
        )

    def test_staff_convenors_returns_correct_number(self):
        self.assertEqual(8, Season.objects.first().staff.convenors().count())
        self.assertEqual(4, League.objects.first().staff.convenors().count())
        self.assertEqual(2, Division.objects.first().staff.convenors().count())

    def test_incorrect_model_staff_convenors_raises_typeerror(self):
        error = "convenors is available on the Season, League, or Division instance."
        self.assertRaisesMessage(
            TypeError, error, SubDivision.objects.first().staff.convenors
        )
        self.assertRaisesMessage(TypeError, error, Team.objects.first().staff.convenors)

    def test_staff_coaches_returns_correct_number(self):
        self.assertEqual(16, Season.objects.first().staff.coaches().count())
        self.assertEqual(8, League.objects.first().staff.coaches().count())
        self.assertEqual(4, Division.objects.first().staff.coaches().count())
        self.assertEqual(2, SubDivision.objects.first().staff.coaches().count())
        self.assertEqual(1, Team.objects.first().staff.coaches().count())

    def test_staff_managers_returns_correct_number(self):
        self.assertEqual(1, Team.objects.first().staff.managers().count())

    def test_incorrect_model_staff_managers_raises_typeerror(self):
        error = "managers is available on the Team instance."
        self.assertRaisesMessage(
            TypeError, error, Season.objects.first().staff.managers
        )
        self.assertRaisesMessage(
            TypeError, error, League.objects.first().staff.managers
        )
        self.assertRaisesMessage(
            TypeError, error, Division.objects.first().staff.managers
        )
        self.assertRaisesMessage(
            TypeError, error, SubDivision.objects.first().staff.managers
        )

    def test_emails_returns_list_of_values(self):
        team = Team.objects.first()
        emails = team.staff.emails()
        self.assertEqual(team.staff.count(), emails.count())
        for email in emails:
            self.assertIsInstance(email, str)
            self.assertIn("@domain.com", email)

    def test_emails_returns_list_of_values_without_blanks(self):
        team = Team.objects.first()
        staff = team.staff.first()
        staff.user.email = "test"
        staff.user.save()
        emails = team.staff.emails()
        self.assertEqual(team.staff.count() - 1, emails.count())
        for email in emails:
            self.assertIsInstance(email, str)
            self.assertIn("@domain.com", email)


class TeamTests(FixtureBasedTestCase):
    def test_team_is_approved_with_hcid_and_status_approved(self):
        team = Team.objects.first()
        self.assertEqual("Fixture Approved", team.status.name)
        self.assertFalse(team.is_approved)
        team.hockey_canada_id = 12345
        self.assertFalse(team.is_approved)
        team.status.considered_approved = True
        self.assertTrue(team.is_approved)

    def test_team_full_name_includes_parent_object_names(self):
        team = Team.objects.first()
        values = [
            str(team.league),
            str(team.division),
            str(team.subdivision),
            str(team.name),
        ]

        expected_base_output = " / ".join(values)
        self.assertEqual(expected_base_output, team.get_full_name())

        expected_custom_output = " * ".join(values)
        self.assertEqual(expected_custom_output, team.get_full_name(" * "))


class TeamStatusTests(TestCase):
    def setUp(self) -> None:
        self.team_status = TeamStatus.objects.create(name="test")
        self.team_status2 = TeamStatus.objects.create(name="test 2")
        return super().setUp()

    def test_teamstatus_uniqueness(self):
        self.assertRaises(IntegrityError, TeamStatus.objects.create, name="test")

    def test_teamstatus_uniqueness_case_insensitive(self):
        self.assertRaises(IntegrityError, TeamStatus.objects.create, name="Test")

    def test_teamstatusreason_uniqueness(self):
        self.team_status.reasons.create(name="test1", default=True)
        self.team_status.reasons.create(name="test3")
        self.team_status.reasons.create(name="test4")

        self.team_status2.reasons.create(name="test1")

        self.assertRaises(
            IntegrityError, self.team_status.reasons.create, name="test2", default=True
        )

    def test_teamstatusreason_uniqueness_is_limited_to_specific_stats(self):
        self.team_status.reasons.create(name="test1")
        self.team_status2.reasons.create(name="test1")

    def test_teamstatusreason_uniqueness_case_insensitive(self):
        self.team_status.reasons.create(name="test1")
        self.assertRaises(IntegrityError, self.team_status.reasons.create, name="test1")

    def test_teamstatusreason_default_is_always_none_due_to_unique_constraint(self):
        tsr = TeamStatusReason.objects.create(
            name="test", default=False, status=self.team_status
        )
        tsr.refresh_from_db()
        self.assertIsNone(tsr.default)


class PlayerPositionTests(TestCase):
    def test_name_uniqueness(self):
        PlayerPosition.objects.create(name="test")
        self.assertRaises(IntegrityError, PlayerPosition.objects.create, name="test")

    def test_name_uniqueness_case_insensitive(self):
        PlayerPosition.objects.create(name="test")
        self.assertRaises(IntegrityError, PlayerPosition.objects.create, name="Test")


class PlayerTypeTests(TestCase):
    def test_name_uniqueness(self):
        PlayerType.objects.create(name="test")
        self.assertRaises(IntegrityError, PlayerType.objects.create, name="test")

    def test_name_uniqueness_case_insensitive(self):
        PlayerType.objects.create(name="test")
        self.assertRaises(IntegrityError, PlayerType.objects.create, name="Test")

    def test_default_unique(self):
        PlayerType.objects.create(name="test", default=True)
        self.assertRaises(
            IntegrityError, PlayerType.objects.create, name="test 2", default=True
        )

    def test_default_is_always_none_due_to_unique_constraint(self):
        pt = PlayerType.objects.create(
            name="test",
            default=False,
        )
        self.assertIsNone(pt.default)


class PlayerStatusTests(TestCase):
    def test_uniqueness(self):
        PlayerStatus.objects.create(name="test")
        self.assertRaises(IntegrityError, PlayerStatus.objects.create, name="test")

    def test_uniqueness_case_insensitive(self):
        PlayerStatus.objects.create(name="test")
        self.assertRaises(IntegrityError, PlayerStatus.objects.create, name="Test")

    def test_default_unique(self):
        PlayerStatus.objects.create(name="test", default=True)
        self.assertRaises(
            IntegrityError, PlayerStatus.objects.create, name="test 2", default=True
        )

    def test_default_is_always_none_due_to_unique_constraint(self):
        pt = PlayerStatus.objects.create(
            name="test",
            default=False,
        )
        self.assertIsNone(pt.default)


class PlayerStatusReasonTests(TestCase):
    def test_uniqueness_case_insensitive(self):
        ps = PlayerStatus.objects.create(name="test")
        ps.reasons.create(name="test")
        self.assertRaises(IntegrityError, ps.reasons.create, name="Test")

    def test_uniqueness(self):
        ps = PlayerStatus.objects.create(name="test")
        ps2 = PlayerStatus.objects.create(name="test 2")

        ps.reasons.create(name="test")
        ps2.reasons.create(name="test")

        self.assertRaises(IntegrityError, ps.reasons.create, name="Test")

    def test_uniqueness_with_default(self):
        ps = PlayerStatus.objects.create(name="test")

        ps.reasons.create(name="test1", default=True)

        self.assertRaises(
            IntegrityError, ps.reasons.create, name="test 2", default=True
        )

    def test_default_is_always_none_due_to_unique_constraint(self):
        ps = PlayerStatus.objects.create(name="test")
        reason = ps.reasons.create(name="test1", default=False)
        self.assertIsNone(reason.default)


class PlayerTests(FixtureBasedTestCase):
    def test_can_create_using_only_team_object(self):
        member = Member.objects.first()
        status = PlayerStatus.objects.filter(reasons__default=True).first()
        pos = PlayerPosition.objects.first()
        ptype = PlayerType.objects.first()

        team = Team.objects.first()

        player = Player.objects.create(
            team=team,
            member=member,
            status=status,
            position=pos,
            type=ptype,
        )
        self.assertEqual(str(player.member), str(player))

    def test_players_counts_on_parent_object(self):
        member = Member.objects.first()
        status = PlayerStatus.objects.filter(reasons__default=True).first()
        pos = PlayerPosition.objects.first()
        ptype = PlayerType.objects.first()

        team = Team.objects.first()

        self.assertEqual(0, team.season.players.count())
        self.assertEqual(0, team.league.players.count())
        self.assertEqual(0, team.division.players.count())
        self.assertEqual(0, team.subdivision.players.count())
        self.assertEqual(0, team.players.count())

        Player.objects.create(
            team=team,
            member=member,
            status=status,
            position=pos,
            type=ptype,
        )
        self.assertEqual(1, team.season.players.count())
        self.assertEqual(1, team.league.players.count())
        self.assertEqual(1, team.division.players.count())
        self.assertEqual(1, team.subdivision.players.count())
        self.assertEqual(1, team.players.count())
        self.assertEqual(0, team.players.affiliates().count())
        self.assertEqual(1, team.players.primary().count())

    def test_player_can_be_on_team_once(self):
        member = Member.objects.first()
        status = PlayerStatus.objects.filter(reasons__default=True).first()
        pos = PlayerPosition.objects.first()
        ptype = PlayerType.objects.first()

        team = Team.objects.first()

        Player.objects.create(
            team=team,
            member=member,
            status=status,
            position=pos,
            type=ptype,
        )
        self.assertRaises(
            IntegrityError,
            Player.objects.create,
            team=team,
            member=member,
            status=status,
            position=pos,
            type=ptype,
        )

    def test_player_marked_as_affiliate_returns_in_team_players_affiliates_count(self):
        member = Member.objects.first()
        status = PlayerStatus.objects.filter(reasons__default=True).first()
        pos = PlayerPosition.objects.first()
        ptype = PlayerType.objects.first()

        team = Team.objects.first()

        Player.objects.create(
            team=team,
            member=member,
            status=status,
            position=pos,
            type=ptype,
            affiliate=True,
        )
        self.assertEqual(1, team.players.count())
        self.assertEqual(1, team.players.affiliates().count())
        self.assertEqual(0, team.players.primary().count())

    def test_adding_player_with_flag_changing_status_causes_team_player_changed_flag_setting_to_true(
        self,
    ):
        member = Member.objects.first()
        status = PlayerStatus.objects.filter(
            reasons__default=True, change_causes_player_flag_on_team_to_enable=True
        ).first()
        pos = PlayerPosition.objects.first()
        ptype = PlayerType.objects.first()

        team = Team.objects.first()

        player = Player.objects.create(
            team=team,
            member=member,
            status=status,
            position=pos,
            type=ptype,
        )
        self.assertIs(True, player.team.players_has_changed_flag)

    def test_adding_player_without_flag_changing_status_keeps_team_player_changed_flag_setting_as_false(
        self,
    ):
        member = Member.objects.first()
        status = PlayerStatus.objects.filter(
            change_causes_player_flag_on_team_to_enable=False
        ).first()
        status_reason = status.reasons.first()

        pos = PlayerPosition.objects.first()
        ptype = PlayerType.objects.first()

        team = Team.objects.first()

        player = Player.objects.create(
            team=team,
            member=member,
            status=status,
            status_reason=status_reason,
            position=pos,
            type=ptype,
        )
        self.assertIs(False, player.team.players_has_changed_flag)

    def test_editing_player_status_changes_reason(self):
        member = Member.objects.first()
        status = PlayerStatus.objects.filter(reasons__default=True).first()
        new_status = (
            PlayerStatus.objects.filter(reasons__default=True)
            .exclude(pk=status.pk)
            .first()
        )
        pos = PlayerPosition.objects.first()
        ptype = PlayerType.objects.first()

        self.assertIs(True, new_status.reasons.filter(default=True).exists())

        team = Team.objects.first()

        player = Player.objects.create(
            team=team,
            member=member,
            status=status,
            position=pos,
            type=ptype,
        )

        player.status = new_status
        player.save()

        self.assertEqual(1, PlayerStatusLog.objects.count())

        self.assertEqual(player.status_reason, new_status.reasons.first())

    def test_editing_player_status_fails_due_to_non_default_non_assigned_reason(self):
        member = Member.objects.first()
        status = PlayerStatus.objects.filter(reasons__default=True).first()
        new_status = PlayerStatus.objects.exclude(
            pk=status.pk, reasons__default=True
        ).first()
        pos = PlayerPosition.objects.first()
        ptype = PlayerType.objects.first()

        self.assertIs(False, new_status.reasons.filter(default=True).exists())

        team = Team.objects.first()

        player = Player.objects.create(
            team=team,
            member=member,
            status=status,
            position=pos,
            type=ptype,
        )

        player.status = new_status
        self.assertRaises(IntegrityError, player.save)

    def test_new_player_fails_due_to_non_default_non_assigned_reason(self):
        member = Member.objects.first()
        status = PlayerStatus.objects.exclude(reasons__default=True).first()
        pos = PlayerPosition.objects.first()
        ptype = PlayerType.objects.first()

        team = Team.objects.first()

        self.assertRaises(
            IntegrityError,
            Player.objects.create,
            team=team,
            member=member,
            status=status,
            position=pos,
            type=ptype,
        )
