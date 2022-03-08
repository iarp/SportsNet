"""
    See core/utils.py:generate_test_fixture_data to see how fixture file is built.
"""
import uuid

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase, tag
from django.utils import timezone

from .models import (
    Division,
    League,
    PermissionOverrides,
    Season,
    SubDivision,
    Team,
    TeamStaff,
    TeamStaffType,
)
from .perms import add_override_permission, has_perm

User = get_user_model()


class ModelStaffCountsTests(TestCase):

    fixtures = ["core/fixtures/test_fixtures.json"]

    def test_confirm_staff_relationships_return_correct_counts(self):
        base_data = {
            Season: 1,
            League: 1,
            Division: 1,
            SubDivision: 1,
            Team: 1,
        }
        for model, count in base_data.items():
            obj = model.objects.first()
            self.assertEqual(
                count, obj.staff.count(), f"{model} mismatch on staff counter"
            )

    def test_season_staff_direct_returns_all_teamstaff_entries(self):
        season = Season.objects.first()
        self.assertEqual(
            TeamStaff.objects.filter(season=season).count(),
            season.staff_direct.count(),
        )

    def test_league_staff_direct_returns_all_teamstaff_entries(self):
        season = Season.objects.first()
        league = season.leagues.first()
        self.assertEqual(
            TeamStaff.objects.filter(season=season, league=league).count(),
            league.staff_direct.count(),
        )

    def test_division_staff_direct_returns_all_teamstaff_entries(self):
        season = Season.objects.first()
        league = season.leagues.first()
        division = league.divisions.first()
        self.assertEqual(
            TeamStaff.objects.filter(
                season=season, league=league, division=division
            ).count(),
            division.staff_direct.count(),
        )

    def test_subdivision_staff_direct_returns_all_teamstaff_entries(self):
        season = Season.objects.first()
        league = season.leagues.first()
        division = league.divisions.first()
        subdivision = division.subdivisions.first()
        self.assertEqual(
            TeamStaff.objects.filter(
                season=season, league=league, division=division, subdivision=subdivision
            ).count(),
            subdivision.staff_direct.count(),
        )

    def test_team_staff_direct_returns_all_teamstaff_entries(self):
        season = Season.objects.first()
        league = season.leagues.first()
        division = league.divisions.first()
        subdivision = division.subdivisions.first()
        team = subdivision.teams.first()

        self.assertEqual(
            TeamStaff.objects.filter(
                season=season,
                league=league,
                division=division,
                subdivision=subdivision,
                team=team,
            ).count(),
            team.staff.count(),
        )


class TeamStaffAccessTests(TestCase):

    fixtures = ["core/fixtures/test_fixtures.json"]

    def test_teamstaff_str_equals_user_username(self):
        ts = TeamStaff.objects.first()
        self.assertEqual(str(ts.user), str(ts))

    def test_season_staff_returns_one_entry(self):
        season1 = Season.objects.first()
        self.assertEqual(1, season1.staff.count())

    def test_seasonal_admins_can_edit_teams(self):
        season1 = Season.objects.first()
        season2 = Season.objects.exclude(pk=season1.pk).first()
        user1_admin = TeamStaff.objects.get(type__name="Admin", season=season1)
        user2_admin = TeamStaff.objects.get(type__name="Admin", season=season2)

        team1 = season1.teams.first()
        team2 = season2.teams.first()

        self.assertIs(True, team1.can_edit(user1_admin))
        self.assertIs(False, team2.can_edit(user1_admin))

        self.assertIs(False, team1.can_edit(user2_admin))
        self.assertIs(True, team2.can_edit(user2_admin))

    def test_team_method_can_edit_accepts_user_or_teamstaff_objects(self):
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

        team1_convenor = TeamStaff.objects.filter(
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
            TeamStaff.objects.filter(
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

    def test_coach1_with_extra_permissions_teamstafftype_can_edit_team2(self):
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

    def test_coach_cannot_vote(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        self.assertIs(False, team1.can_vote(team1_coach))

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

        TeamStaffType.objects.filter(name="Coach").update(team_can_vote=True)

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

    @tag("slow")
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

    @tag("slow")
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

    @tag("slow")
    def test_vp_only_has_league_permissible_teams(self):
        team1 = Team.objects.first()
        team1_vp = team1.league.staff.first()

        for team in team1.league.teams.all():
            self.assertIs(True, team.can_edit(team1_vp))

        i = 0
        for team in Team.objects.all():
            i += team.can_edit(team1_vp)

        self.assertEqual(team1.league.teams.count(), i)


class PermissionOverrideTests(TestCase):

    fixtures = ["core/fixtures/test_fixtures.json"]

    def test_add_override_adds_one_row(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        self.assertEqual(0, PermissionOverrides.objects.count())

        team1_coach.permissions_add_override(team1.division, "team_can_vote", True)

        self.assertEqual(1, PermissionOverrides.objects.count())

        team1_coach.permissions_add_override(team1.division, "team_can_vote", True)

        self.assertEqual(1, PermissionOverrides.objects.count())

    # def test_add_override_removes_defaults_matching_row(self):
    #     team1 = Team.objects.first()
    #     team1_coach = team1.staff.first()
    #     self.assertEqual(0, PermissionOverrides.objects.count())
    #     team1_coach.permissions_add_override(team1.division, "team_can_vote", True)
    #     self.assertEqual(1, PermissionOverrides.objects.count())
    #     team1_coach.permissions_add_override(team1.division, "team_can_vote", False)
    #     self.assertEqual(0, PermissionOverrides.objects.count())

    def test_add_override_updates_existing_row(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        self.assertEqual(0, PermissionOverrides.objects.count())

        ts = team1_coach.permissions_add_override(team1.division, "team_can_vote", True)

        obj = PermissionOverrides.objects.get()
        self.assertEqual(ts.pk, obj.pk)
        self.assertIs(True, obj.team_can_vote)
        self.assertIs(True, obj.team_can_edit)

        team1_coach.permissions_add_override(team1.division, "team_can_edit", False)

        obj = PermissionOverrides.objects.get()
        self.assertIs(True, obj.team_can_vote)
        self.assertIs(False, obj.team_can_edit)

    def test_add_permission_raises_keyerror_on_invalid_permission_name(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        self.assertRaisesMessage(
            ValueError,
            "Parameter permission_name value must be an attribute of PermissionOverrides model.",
            team1_coach.permissions_add_override,
            team1_coach.division,
            "invalid_name",
            True,
        )

    def test_add_permission_raises_valueerror_on_invalid_object_type(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        self.assertRaisesMessage(
            ValueError,
            "Parameter obj must be of type Season, League, Division, SubDivision, or Team.",
            team1_coach.permissions_add_override,
            team1_coach.user,
            "invalid_name",
            True,
        )

    def test_add_override_does_not_set_assigned_by_when_none(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        team1_coach.permissions_add_override(team1.division, "team_can_vote", True)

        perm = PermissionOverrides.objects.get()

        self.assertIsNone(perm.assigned_by_id)

    def test_add_override_adds_assigned_by_user(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        team1_coach.permissions_add_override(
            team1.division, "team_can_vote", True, team1_coach.user
        )

        perm = PermissionOverrides.objects.get()

        self.assertEqual(team1_coach.user_id, perm.assigned_by_id)

    def test_add_override_adds_assigned_by_teamstaff(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        team1_coach.permissions_add_override(
            team1.division, "team_can_vote", True, team1_coach
        )

        perm = PermissionOverrides.objects.get()

        self.assertEqual(team1_coach.user_id, perm.assigned_by_id)
        self.assertIsNotNone(perm.assigned_on)
        self.assertIsInstance(perm.assigned_on, timezone.datetime)


class CoreUtilsTests(TestCase):

    fixtures = ["core/fixtures/test_fixtures.json"]

    def test_add_override_permission_raises_valueerror_on_invalid_obj_passed(self):
        obj = object()

        team1 = Team.objects.first()
        team1_coach = team1.staff.first()

        self.assertRaisesMessage(
            ValueError,
            "Parameter obj must be of type Season, League, Division, SubDivision, or Team.",
            add_override_permission,
            team1_coach,
            obj,
            "test_can_edit",
            False,
        )

    def test_has_perm_returns_true_for_superuser(self):
        team1_coach = TeamStaff.objects.first()
        team = Team.objects.last()

        self.assertNotEqual(team1_coach.team_id, team.pk)

        self.assertIs(False, has_perm(team1_coach, team, "team_can_edit"))

        team1_coach.user.is_superuser = True

        self.assertIs(True, has_perm(team1_coach, team, "team_can_edit"))


class CoreSignalsTests(TestCase):
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
        self.team = Team.objects.create(
            season=self.season,
            league=self.league,
            division=self.division,
            subdivision=self.subdivision,
            name="Team 1",
        )
        self.stafftype = TeamStaffType.objects.create(name="staff type")

        return super().setUp()

    def create_teamstaff(self, *args, **kwargs):
        return TeamStaff.objects.create(
            user=self.user, type=self.stafftype, *args, **kwargs
        )

    def test_ensure_teamstaff_entry_has_proper_ids_with_season_object(self):
        obj = self.create_teamstaff(season=self.season)
        self.assertEqual(self.season.pk, obj.season_id)
        self.assertIsNone(obj.league_id)
        self.assertIsNone(obj.division_id)
        self.assertIsNone(obj.subdivision_id)
        self.assertIsNone(obj.team_id)

    def test_ensure_teamstaff_entry_has_proper_ids_with_league_object(self):
        obj = self.create_teamstaff(league=self.league)

        self.assertEqual(self.season.pk, obj.season_id)
        self.assertEqual(self.league.pk, obj.league_id)
        self.assertIsNone(obj.division_id)
        self.assertIsNone(obj.subdivision_id)
        self.assertIsNone(obj.team_id)

    def test_ensure_teamstaff_entry_has_proper_ids_with_division_object(self):
        obj = self.create_teamstaff(division=self.division)

        self.assertEqual(self.season.pk, obj.season_id)
        self.assertEqual(self.league.pk, obj.league_id)
        self.assertEqual(self.division.pk, obj.division_id)
        self.assertIsNone(obj.subdivision_id)
        self.assertIsNone(obj.team_id)

    def test_ensure_teamstaff_entry_has_proper_ids_with_subdivision_object(self):
        obj = self.create_teamstaff(subdivision=self.subdivision)

        self.assertEqual(self.season.pk, obj.season_id)
        self.assertEqual(self.league.pk, obj.league_id)
        self.assertEqual(self.division.pk, obj.division_id)
        self.assertEqual(self.subdivision.pk, obj.subdivision_id)
        self.assertIsNone(obj.team_id)

    def test_ensure_teamstaff_entry_has_proper_ids_with_team_object(self):
        obj = self.create_teamstaff(team=self.team)

        self.assertEqual(self.season.pk, obj.season_id)
        self.assertEqual(self.league.pk, obj.league_id)
        self.assertEqual(self.division.pk, obj.division_id)
        self.assertEqual(self.subdivision.pk, obj.subdivision_id)
        self.assertEqual(self.team.pk, obj.team_id)


class SeasonTests(TestCase):
    def setUp(self) -> None:
        year = timezone.now().year - 1

        self.season1 = Season.objects.create(
            name=f"{year}-{year+1}",
            start=timezone.datetime(year, 9, 1).date(),
            end=timezone.datetime(year + 1, 8, 31).date(),
        )

        year += 1

        self.season2 = Season.objects.create(
            name=f"{year}-{year+1}",
            start=timezone.datetime(year, 9, 1).date(),
            end=timezone.datetime(year + 1, 8, 31).date(),
        )

        year += 1

        self.season3 = Season.objects.create(
            name=f"{year}-{year+1}",
            start=timezone.datetime(year, 9, 1).date(),
            end=timezone.datetime(year + 1, 8, 31).date(),
        )

        return super().setUp()

    def test_expected_current_season(self):
        current_season = Season.get_current()
        self.assertIn(current_season, (self.season1, self.season2))

    def test_expected_next_season(self):
        current_season = Season.get_current()
        next_season = current_season.get_next_season()
        if current_season.pk == self.season1.pk:
            self.assertEqual(self.season2, next_season)
        elif current_season.pk == self.season2.pk:
            self.assertEqual(self.season3, next_season)
        else:
            raise ValueError(
                "Failed to match current and next seasons. Do not enable caching on Season.get_current()"
            )

    def test_next_season_returns_none(self):
        self.assertIsNone(self.season3.get_next_season())

    def test_expected_current_season_with_based_on_date(self):
        target_date = timezone.datetime(timezone.now().year, 10, 3)
        current_season = Season.get_current(target_date)
        self.assertEqual(self.season2, current_season)

    def test_expected_current_season_on_last_date(self):
        target_date = timezone.datetime(timezone.now().year, 8, 31)
        current_season = Season.get_current(target_date)
        self.assertEqual(self.season1, current_season)

    def test_expected_current_season_on_first_date(self):
        target_date = timezone.datetime(timezone.now().year, 9, 1)
        current_season = Season.get_current(target_date)
        self.assertEqual(self.season2, current_season)

    def test_current_season_raises_on_season_missing(self):
        target_date = timezone.datetime(timezone.now().year + 6, 9, 1)
        self.assertRaisesMessage(
            Season.DoesNotExist,
            "Season matching query does not exist.",
            Season.get_current,
            target_date,
        )

    # Replaced with ValueError exception in Season.save to prevent overlapping
    # def test_current_season_raises_on_seasons_overlapping_dates(self):
    #     year = timezone.now().year
    #     start = timezone.datetime(year - 1, 1, 1)
    #     end = timezone.datetime(year + 1, 1, 1)
    #     Season.objects.create(name="season1", start=start, end=end)
    #     Season.objects.create(name="season2", start=start, end=end)
    #     self.assertRaisesMessage(
    #         Season.MultipleObjectsReturned,
    #         "get() returned more than one Season -- it returned 3!",
    #         Season.get_current,
    #         timezone.datetime(year, 10, 3),
    #     )

    def test_previous_season_returns_none_on_first_season(self):
        self.assertIsNone(self.season1.get_previous_season())

    def test_expected_previous_season(self):
        self.assertEqual(self.season1, self.season2.get_previous_season())
        self.assertEqual(self.season2, self.season3.get_previous_season())

    def test_season_creation_raises_integrityerror_with_end_before_start(self):
        today = timezone.now() + timezone.timedelta(days=365 * 6)

        self.assertRaises(
            IntegrityError,
            Season.objects.create,
            name="test",
            start=today,
            end=today - timezone.timedelta(days=15),
        )

    def test_new_season_save_raises_exception_when_dates_within_another_seasons_daterange(
        self,
    ):
        Season.objects.create(
            name="test 1",
            start=timezone.datetime(2000, 1, 1).date(),
            end=timezone.datetime(2000, 12, 31).date(),
        )
        Season.objects.create(
            name="test 2",
            start=timezone.datetime(2001, 1, 1).date(),
            end=timezone.datetime(2002, 12, 31).date(),
        )

        self.assertRaisesMessage(
            ValueError,
            "Season start and end dates cannot be between another seasons dates.",
            Season.objects.create,
            name="test1",
            start=timezone.datetime(2000, 3, 1).date(),
            end=timezone.datetime(2003, 12, 31).date(),
        )

    def test_get_current_raises_exception_on_invalid_object(self):
        self.assertRaises(
            TypeError,
            Season.get_current,
            object(),
        )

    def test_season_hockey_canada_id_unique(self):
        self.season1.hockey_canada_id = 2022123456789
        self.season1.save()

        self.season2.hockey_canada_id = 2022123456789

        self.assertRaises(
            IntegrityError,
            self.season2.save,
        )

    def test_season_hockey_canada_system_id_unique(self):
        system_id = str(uuid.uuid4())
        self.season1.hockey_canada_system_id = system_id
        self.season1.save()

        self.season2.hockey_canada_system_id = system_id

        self.assertRaises(
            IntegrityError,
            self.season2.save,
        )


class CoreUserTests(TestCase):
    def test_user_username_always_matches_email(self):
        user = User.objects.create(email="test@domain.com")
        self.assertEqual(user.email, user.username)

        user.username = "test"
        user.save()
        self.assertEqual(user.email, user.username)
