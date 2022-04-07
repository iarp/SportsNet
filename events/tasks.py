# Create your tasks here
from __future__ import absolute_import, unicode_literals

from django.core.management import call_command

from sportsnet.celery import app


@app.task(bind=True)
def get_tournament_listings(self):
    call_command("get_tournament_listing")
