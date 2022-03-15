from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy
from positions.fields import PositionField

from core.model_helpers import _BaseModel


class DocumentCategory(_BaseModel):
    class Meta:
        ordering = ["name"]
        verbose_name = gettext_lazy("Document Category")
        verbose_name_plural = gettext_lazy("Document Categories")
        constraints = [
            models.UniqueConstraint(
                Lower("name"), name="documentcategory_name_uniqueness"
            )
        ]

    name = models.CharField(max_length=255)


class DocumentType(_BaseModel):
    class Meta:
        ordering = ["category", "name"]
        verbose_name = gettext_lazy("Document Type")
        verbose_name_plural = gettext_lazy("Document Types")
        constraints = [
            models.UniqueConstraint(
                Lower("name"), "category", name="documenttype_name_category_uniqueness"
            )
        ]

    name = models.CharField(max_length=255)
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE)


class DocumentLevel(_BaseModel):
    class Meta:
        ordering = ["type", "name"]
        verbose_name = gettext_lazy("Document Level")
        verbose_name_plural = gettext_lazy("Document Levels")
        constraints = [
            models.UniqueConstraint(
                Lower("name"), "type", name="documentevel_name_type_uniqueness"
            )
        ]

    name = models.CharField(max_length=255)
    type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)


class DocumentEquivilent(_BaseModel):
    class Meta:
        ordering = ["name"]
        verbose_name = gettext_lazy("Document Equivilent")
        verbose_name_plural = gettext_lazy("Document Equivilents")
        constraints = [
            models.UniqueConstraint(
                Lower("name"), name="documentequivilent_name_uniqueness"
            )
        ]

    name = models.CharField(max_length=255)


class DocumentEquivilentDtl(_BaseModel):
    class Meta:
        ordering = ["equivilent", "name", "level"]
        verbose_name = gettext_lazy("Document Equivilent DTL?")
        verbose_name_plural = gettext_lazy("Document Equivilents DTL?")
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "equivilent",
                "level",
                name="documentequivilentdtl_name_equivilent_level_uniqueness",
            )
        ]

    equivilent = models.ForeignKey(DocumentEquivilent, on_delete=models.CASCADE)
    level = models.ForeignKey(DocumentLevel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class Qualification(_BaseModel):
    name = models.CharField(max_length=255)


class QualificationRule(_BaseModel):
    name = models.CharField(max_length=255)
    qualification = models.ForeignKey(
        Qualification, on_delete=models.CASCADE, related_name="rules"
    )

    weight = PositionField(collection="qualification")
    LogicOperationId = models.IntegerField(default=1)

    document_level = models.ForeignKey(
        DocumentLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    document_equivilent = models.ForeignKey(
        DocumentEquivilent, on_delete=models.CASCADE, related_name="qualification_rules"
    )
