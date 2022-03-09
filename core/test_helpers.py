from django.test import TestCase


class FixtureBasedTestCase(TestCase):

    fixtures = ["core/fixtures/test_fixtures.json", "team/fixtures/test_fixtures.json"]
