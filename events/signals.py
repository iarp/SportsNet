from django.db.models.signals import post_save

from events.models import Tournament

# from travelpermits.models import TravelPermit


def tournament_verified_update_permits(instance: Tournament, **kwargs):
    if instance.verified:
        for permit in instance.travelpermit_set.filter(
            status=TravelPermit.SYSTEM_WAIT_TOURNAMENT_VERIFICATION
        ):
            permit.tournament_has_been_verified()


post_save.connect(tournament_verified_update_permits, Tournament)
