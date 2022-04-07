from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils import timezone

from .models import Association, Rink, Tournament

# from core.test_helpers import FixtureBasedTestCase

User = get_user_model()


class AssociationTests(TestCase):
    def test_name_uniqueness(self):
        Association.objects.create(name="test")
        self.assertRaises(IntegrityError, Association.objects.create, name="test")

    def test_name_uniqueness_case_insensitive(self):
        Association.objects.create(name="test")
        self.assertRaises(IntegrityError, Association.objects.create, name="Test")


class RinkTests(TestCase):
    def test_name_city_province_uniqueness(self):
        Rink.objects.create(name="test", city="test", province="test")
        self.assertRaises(
            IntegrityError,
            Rink.objects.create,
            name="test",
            city="test",
            province="test",
        )

    def test_name_city_province_uniqueness_case_insensitive(self):
        Rink.objects.create(
            name="test",
            city="test",
            province="test",
        )
        self.assertRaises(
            IntegrityError,
            Rink.objects.create,
            name="Test",
            city="test",
            province="test",
        )


class TournamentViewsTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="test@domain.com", password="12345")
        self.client.force_login(self.user)

        self.association = Association.objects.create(name="test")

        return super().setUp()

    def test_tournament_creation(self):
        tourn_name = "Test Tournament"
        data = {
            "name": tourn_name,
            "sanction_number": "",
            "location": "location",
            "start_date": timezone.now().date().strftime("%Y-%m-%d"),
            "end_date": "",
            "association": self.association.pk,
            "website": "",
        }
        try:
            self.client.post(reverse("events:tournament-new"), data=data)
            exception_message = False
        except NoReverseMatch as e:
            exception_message = e

        # NOTE: Remove once travelpermits app is in place
        self.assertIn(
            "'travelpermits' is not a registered namespace",
            str(exception_message),
            "If travelpermits has been implemented, remove this check and the preceding try/except block.",
        )

        tournament = Tournament.objects.first()
        self.assertEqual(tourn_name, tournament.name)

    def test_tournament_listing(self):

        Tournament.objects.create(
            association=self.association,
            name="test tournament name",
            location="",
            start_date=timezone.datetime.now().date(),
        )

        resp = self.client.get(reverse("events:tournaments-list"))

        self.assertEqual(200, resp.status_code)

        self.assertContains(resp, b"test tournament name", 1)


class ExhibitionViewsTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="test@domain.com", password="12345")
        self.client.force_login(self.user)

        self.association = Association.objects.create(name="test")
        return super().setUp()

    def test_exhibition_listing(self):

        resp = self.client.get(reverse("events:exhibitions-list"))

        self.assertEqual(200, resp.status_code)
