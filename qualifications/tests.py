from django.db.utils import IntegrityError
from django.test import TestCase

from .models import (
    DocumentCategory,
    DocumentEquivilent,
    DocumentEquivilentDtl,
    DocumentLevel,
    DocumentType,
)


class DocumentCategoryTests(TestCase):
    def test_name_uniqueness(self):
        DocumentCategory.objects.create(name="test")
        self.assertRaises(IntegrityError, DocumentCategory.objects.create, name="test")

    def test_name_uniqueness_case_insensitive(self):
        DocumentCategory.objects.create(name="test")
        self.assertRaises(IntegrityError, DocumentCategory.objects.create, name="Test")


class DocumentEquivilentTests(TestCase):
    def test_name_uniqueness(self):
        DocumentEquivilent.objects.create(name="test")
        self.assertRaises(
            IntegrityError, DocumentEquivilent.objects.create, name="test"
        )

    def test_name_uniqueness_case_insensitive(self):
        DocumentEquivilent.objects.create(name="test")
        self.assertRaises(
            IntegrityError, DocumentEquivilent.objects.create, name="Test"
        )


class DocumentEquivilentDtlTests(TestCase):
    def test_name_uniqueness(self):
        dc = DocumentCategory.objects.create(name="test")
        dt = DocumentType.objects.create(category=dc, name="test")
        dl = DocumentLevel.objects.create(type=dt, name="test")
        de = DocumentEquivilent.objects.create(name="test")
        DocumentEquivilentDtl.objects.create(level=dl, equivilent=de, name="test")
        self.assertRaises(
            IntegrityError,
            DocumentEquivilentDtl.objects.create,
            level=dl,
            equivilent=de,
            name="test",
        )


class DocumentTypeTests(TestCase):
    def test_name_uniqueness(self):
        dc = DocumentCategory.objects.create(name="test")
        DocumentType.objects.create(category=dc, name="test")
        self.assertRaises(
            IntegrityError, DocumentType.objects.create, category=dc, name="test"
        )

    def test_name_uniqueness_case_insensitive(self):
        dc = DocumentCategory.objects.create(name="test")
        DocumentType.objects.create(category=dc, name="test")
        self.assertRaises(
            IntegrityError, DocumentType.objects.create, category=dc, name="Test"
        )


class DocumentLevelTests(TestCase):
    def test_name_uniqueness(self):
        dc = DocumentCategory.objects.create(name="test")
        dt = DocumentType.objects.create(category=dc, name="test")
        DocumentLevel.objects.create(type=dt, name="test")
        self.assertRaises(
            IntegrityError, DocumentLevel.objects.create, type=dt, name="test"
        )

    def test_name_uniqueness_case_insensitive(self):
        dc = DocumentCategory.objects.create(name="test")
        dt = DocumentType.objects.create(category=dc, name="test")
        DocumentLevel.objects.create(type=dt, name="test")
        self.assertRaises(
            IntegrityError, DocumentLevel.objects.create, type=dt, name="Test"
        )
