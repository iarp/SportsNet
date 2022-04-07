import logging

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_templated_emailer.models import EmailQueue

import events.association_profiles
from browser import SKBrowserBase
from events.models import Association, Tournament
from project_settings import proj_settings

log = logging.getLogger("events.commands.get_tournament_listing")


class Command(BaseCommand):
    help = "Loads tournaments from Associations that have a tournament listing page"

    def handle(self, *args, **options):
        browser = None

        # Tournament.objects.filter(created__date=timezone.now().date()).delete()

        tournaments_with_incorrect_dates = []

        for association in Association.objects.exclude(tournament_listing_url=""):

            profile = getattr(events.association_profiles, association.name, None)
            if not profile:
                self.stdout.write(f"Scanner profile for {association} not found.")
                continue
            elif not profile.ENABLED:
                self.stdout.write(f"Scanner profile disabled for {association}")
                continue

            if not browser:
                browser = SKBrowserBase()

            self.stdout.write(f"{association} {association.tournament_listing_url}")

            browser.load_url(association.tournament_listing_url)

            try:
                rows = profile.scan(browser, association)
            except:
                log.exception(f"Scan failure on {association}")
                continue

            if rows is None:
                self.stdout.write(
                    f"See log for details on {association} as something went wrong."
                )
                continue

            self.stdout.write(f"{association} found {len(rows)} tournaments.")

            for row_data in rows:

                # If the End Date comes BEFORE the Start Date, check if the Day and
                # Month between both dates are the same. If they match, its more than
                # likely just an invalid year value.
                # 2019-10-30: Disabled for the time being, too many incorrect dates coming from OMHA.
                # if row_data['Start Date'] > row_data['End Date']:
                #     print(row_data)
                #
                #     if row_data['Start Date'].day == row_data['End Date'].day and \
                #             row_data['Start Date'].month == row_data['End Date'].month:
                #         row_data['End Date'] = row_data['End Date'].replace(year=row_data['Start Date'].year)
                #
                #     print(row_data)

                try:
                    defaults = {
                        "name": row_data["Tournament Name"],
                        "location": row_data["Centre"],
                        "divisions": row_data["Divisions"],
                        "start_date": row_data["Start Date"],
                        "end_date": row_data["End Date"],
                        "verified": True,
                        "verified_date": timezone.now(),
                        "source": "tournament_listing_url",
                        "website": association.tournament_listing_url,
                        "notes": "Added by get_tournament_listing command",
                    }

                    t, was_created = Tournament.objects.get_or_create(
                        association=association,
                        sanction_number=row_data["Sanction Number"],
                        defaults=defaults,
                    )

                    # No longer saving updates due to us having to manually edit End Date's
                    # if not was_created:
                    #     core_data.base_functions.only_save_changed(
                    #         obj=t,
                    #         defaults=defaults,
                    #         not_these_fields=['notes', 'verified_date']
                    #     )

                    # If the End date comes BEFORE the start date, email someone about it.
                    if was_created and t.start_date > t.end_date:
                        tournaments_with_incorrect_dates.append(t)

                except Tournament.MultipleObjectsReturned:
                    log.warning(
                        f"{association} returned multiple records for a Tournament sanction {row_data['Sanction Number']}"
                    )

                except KeyError:
                    log.debug(row_data)
                    log.exception(
                        f"Stopped processing association {association} as there is something wrong."
                    )
                    break

        if tournaments_with_incorrect_dates:
            EmailQueue.queue_email(
                template_name="System - Event Scanner - Invalid Dates Found",
                domain=proj_settings.DOMAIN_BASE,
                tournaments=tournaments_with_incorrect_dates,
            )

        if browser:
            browser.quit()
