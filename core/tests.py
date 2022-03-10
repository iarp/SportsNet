"""
    See core/utils.py:generate_test_fixture_data to see how fixture file is built.
"""
import uuid

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from team.models import Staff, StaffType, Team

from .models import League, PermissionOverrides, Season
from .perms import add_override_permission, has_perm
from .test_helpers import FixtureBasedTestCase

User = get_user_model()


class PermissionOverrideTests(FixtureBasedTestCase):
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

    def test_add_override_adds_assigned_by_staff(self):
        team1 = Team.objects.first()

        team1_coach = team1.staff.first()

        team1_coach.permissions_add_override(
            team1.division, "team_can_vote", True, team1_coach
        )

        perm = PermissionOverrides.objects.get()

        self.assertEqual(team1_coach.user_id, perm.assigned_by_id)
        self.assertIsNotNone(perm.assigned_on)
        self.assertIsInstance(perm.assigned_on, timezone.datetime)


class CoreUtilsTests(FixtureBasedTestCase):
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
        team1_coach = Staff.objects.first()
        team = Team.objects.last()

        self.assertNotEqual(team1_coach.team_id, team.pk)

        self.assertIs(False, has_perm(team1_coach, team, "team_can_edit"))

        team1_coach.user.is_superuser = True

        self.assertIs(True, has_perm(team1_coach, team, "team_can_edit"))


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

    def test_name_uniqueness(self):
        self.assertRaises(
            IntegrityError,
            Season.objects.create,
            name=self.season1.name,
            start=timezone.now() + timezone.timedelta(days=5 * 365),
            end=timezone.now() + timezone.timedelta(days=6 * 365),
        )


class LeagueTests(FixtureBasedTestCase):
    def test_league_season_name_uniqueness(self):
        season = Season.objects.first()
        self.assertRaises(
            IntegrityError, League.objects.create, season=season, name="HL"
        )

    def test_league_season_name_uniqueness_case_insensitve(self):
        season = Season.objects.first()
        self.assertRaises(
            IntegrityError, League.objects.create, season=season, name="Hl"
        )

    def test_league_creates_successfully_on_new_season(self):
        season = Season.objects.create(
            name="test",
            start=timezone.now() + timezone.timedelta(days=5 * 365),
            end=timezone.now() + timezone.timedelta(days=6 * 365),
        )
        League.objects.create(season=season, name="HL")


class CoreUserTests(FixtureBasedTestCase):
    def test_user_username_always_matches_email(self):
        user = User.objects.first()
        self.assertEqual(user.email, user.username)

        user.username = "test"
        user.save()
        self.assertEqual(user.email, user.username)

    def test_user_can_login_with_web_access_true_on_staff_type(self):

        StaffType.objects.filter(name="Coach").update(web_access=True)

        user = User.objects.filter(staff_assignments__type__web_access=True).first()

        response = self.client.post(
            reverse("account_login"),
            {"login": user.email, "password": "12345"},
            follow=True,
        )
        self.assertEqual(user.pk, response.context["user"].pk)

    def test_user_cannot_login_with_web_access_false_on_staff_type(self):

        user = User.objects.all().first()

        self.assertIs(
            False, user.staff_assignments.filter(type__web_access=True).exists()
        )

        response = self.client.post(
            reverse("account_login"),
            {"login": user.email, "password": "12345"},
            follow=True,
        )
        self.assertIsNone(response.context["user"].pk)

    def test_login_does_not_throw_error_if_password_is_incorrect(self):

        user = User.objects.all().first()

        response = self.client.post(
            reverse("account_login"),
            {"login": user.email, "password": "invalid password"},
            follow=True,
        )
        self.assertIsNone(response.context["user"].pk)
