from django.db import models
from django.db.models import Q
from django.utils.translation import gettext, gettext_lazy


class _StaffObjectsManagerWithDetails(models.Manager):
    def head_coach(self, *args, **kwargs):
        if self.instance.__class__.__name__ == "Team":
            return self.filter(*args, type__name="Coach", **kwargs).first()
        raise TypeError(gettext_lazy("head_coach is available on the Team instance."))

    def own(self, *args, **kwargs):
        instance_type = self.instance.__class__.__name__
        extras = {}
        if instance_type == "Season":
            extras = {
                "league_id__isnull": True,
                "division_id__isnull": True,
                "subdivision_id__isnull": True,
                "team_id__isnull": True,
            }
        elif instance_type == "League":
            extras = {
                "division_id__isnull": True,
                "subdivision_id__isnull": True,
                "team_id__isnull": True,
            }
        elif instance_type == "Division":
            extras = {
                "subdivision_id__isnull": True,
                "team_id__isnull": True,
            }
        elif instance_type == "SubDivision":
            extras = {
                "team_id__isnull": True,
            }
        return self.filter(*args, **extras, **kwargs)

    def vps(self):
        if self.instance.__class__.__name__ == "Season":
            return self.filter(
                division_id__isnull=True,
                subdivision_id__isnull=True,
                team_id__isnull=True,
            ).exclude(league_id__isnull=True)
        raise TypeError(gettext("vps is available on the Season instance."))

    def senior_convenors(self):
        if self.instance.__class__.__name__ == "Season":
            return self.filter(
                subdivision_id__isnull=True,
                team_id__isnull=True,
            ).exclude(Q(league_id__isnull=True) | Q(division_id__isnull=True))
        elif self.instance.__class__.__name__ == "League":
            return self.filter(
                subdivision_id__isnull=True,
                team_id__isnull=True,
            ).exclude(Q(league_id__isnull=True) | Q(division_id__isnull=True))
        raise TypeError(
            gettext("senior_convenors is available on the Season or League instance.")
        )

    def convenors(self):
        if self.instance.__class__.__name__ == "Season":
            return self.filter(team_id__isnull=True).exclude(
                Q(league_id__isnull=True)
                | Q(division_id__isnull=True)
                | Q(subdivision_id__isnull=True)
            )
        elif self.instance.__class__.__name__ == "League":
            return self.filter(team_id__isnull=True).exclude(
                Q(division_id__isnull=True) | Q(subdivision_id__isnull=True)
            )
        elif self.instance.__class__.__name__ == "Division":
            return self.filter(team_id__isnull=True).exclude(
                subdivision_id__isnull=True,
            )
        raise TypeError(
            gettext(
                "convenors is available on the Season, League, or Division instance."
            )
        )

    def coaches(self):
        return self.filter(type__name="Coach")
        # if isinstance(self.instance, Season):
        #     return qs.exclude(
        #         Q(league_id__isnull=True)
        #         | Q(division_id__isnull=True)
        #         | Q(subdivision_id__isnull=True)
        #         | Q(team_id__isnull=True)
        #     )
        # elif isinstance(self.instance, League):
        #     return qs.exclude(
        #         Q(division_id__isnull=True)
        #         | Q(subdivision_id__isnull=True)
        #         | Q(team_id__isnull=True)
        #     )
        # elif isinstance(self.instance, Division):
        #     return qs.exclude(Q(subdivision_id__isnull=True) | Q(team_id__isnull=True))
        # elif isinstance(self.instance, SubDivision):
        #     return qs.exclude(team_id__isnull=True)
        # raise TypeError(
        #     gettext("coaches is available on the Season, League, Division, or SubDivision instance.")
        # )

    def managers(self):
        if self.instance.__class__.__name__ == "Team":
            return self.filter(type__name="Manager")
        raise TypeError(gettext("managers is available on the Team instance."))


class _StaffManagerCustomQuerySet(models.QuerySet):
    def emails(self):
        return self.filter(user__email__contains="@").values_list(
            "user__email", flat=True
        )
