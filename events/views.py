from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    HttpResponse,
    HttpResponseRedirect,
    get_object_or_404,
    redirect,
    render,
    resolve_url,
)
from django.utils import timezone

from core.utils import redirect_next
from events.forms import NewExhibitionForm, NewTournamentForm
from events.models import Exhibition, Tournament
from team.helpers import add_selected_team


@login_required
def event_list(request, event_type="tournament"):
    """Lists all events (Tournament or Exhibition) depending on event_type value."""

    events = Tournament.objects.select_related("association")
    if event_type.lower() == "exhibition":
        events = Exhibition.objects.select_related("other_team_association", "rink")

    events = events.filter(start_date__gte=timezone.now())
    # .prefetch_related(
    #    "travelpermit_set"
    # )

    return render(
        request,
        "events/events.html",
        {
            "event_type": event_type,
            "events": events.order_by("start_date"),
        },
    )


@login_required
def event_new(request, event_type):
    """Creates a new tournament or exhibition"""

    form = NewTournamentForm(request.POST or None)
    if event_type == "exhibition":
        form = NewExhibitionForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():
            instance = form.save(commit=False)  # type: Tournament
            instance.inserted_by = request.user
            instance.source = f"{event_type}_new"

            save_event = True
            tourns = None

            if isinstance(instance, Tournament):

                if instance.sanction_number and instance.association.name not in [
                    "OTHER"
                ]:

                    tourns = Tournament.objects.filter(
                        association=instance.association,
                        sanction_number=instance.sanction_number,
                    )

                    save_event = not tourns.exists()

            if save_event:
                instance.save()

            elif tourns and tourns.exists():
                instance = tourns.first()

            else:
                messages.error(request, "System Error Occurred. Contact the office.")

            if not len(messages.get_messages(request=request)):
                # return redirect(f'events:{event_type}-details', event_id=instance.id)
                return redirect(
                    f"travelpermits:permit-new-{event_type}",
                    event_id=instance.id,
                )

    return render(
        request,
        "events/event_new.html",
        {
            "event_type": event_type,
            "form": form,
        },
    )


@login_required
@add_selected_team
def event_details(request, event_type, event_id, selected):

    if event_type == "exhibition":
        event = get_object_or_404(
            Exhibition.objects.select_related("other_team_association", "rink"),
            pk=event_id,
        )
    else:
        event = get_object_or_404(
            Tournament.objects.select_related("association"), pk=event_id
        )

    team = SportsKeeperTeam(load_ids_from=selected) if selected.TeamId else None

    return render(
        request,
        "events/event_details.html",
        {
            "event": event,
            "event_type": event_type,
            "permits": event.travelpermit_set.all(),
            "team_already_has_permit": event.travelpermit_set.filter(
                team_id=selected.TeamId
            ).exists(),
            "team": team,
            "team_is_approved": team.is_approved() if team else False,
        },
    )


@login_required
def tournament_verification(request, event_id):
    """
    Tournaments added by anyone except office personnel will require confirmation
        that said tournament exists. Only allow those with permission to validate tournaments here.
    """

    event = get_object_or_404(Tournament, pk=event_id)

    if not event.sanction_number:
        if request.method == "POST":
            return HttpResponse("Failure: Sanction Number Required.")
        messages.info(request, "Tournaments must have sanction number!")
    else:
        event.has_been_verified()

    if request.method == "POST":
        return HttpResponse("Success: Verified!")

    if request.GET.get("next"):
        return HttpResponseRedirect(request.GET["next"])

    return redirect("events:tournament-details", event_id=event.id)


@login_required
def tournaments_needing_verification(request):
    return render(
        request,
        "events/tournament_verification.html",
        {
            "tournaments": Tournament.objects.filter(verified=False),
        },
    )


@login_required
def tournament_edit(request, event_id):
    """Edits an existing tournament"""

    instance = get_object_or_404(Tournament, pk=event_id)

    if not instance.can_edit():
        messages.error(
            request,
            "Permit(s) attached to this event have already been submitted to the OMHA.",
        )
        return redirect("events:tournament-details", event_id=instance.id)

    form = NewTournamentForm(request.POST or None, instance=instance)

    if request.method == "POST" and form.is_valid():

        if request.POST.get("delete"):
            instance.delete()
            return redirect("events:tournaments-list")
        else:
            form.save()

        return redirect_next(request, "events:tournament-needs-verification")

    return render(
        request,
        "events/event_new.html",
        {
            "event_type": "tournament",
            "form": form,
            "editing": True,
        },
    )


@login_required
def exhibition_edit(request, event_id):
    """Edits an existing exhibition"""

    instance = get_object_or_404(Exhibition, pk=event_id)

    if not instance.can_edit():
        messages.error(
            request,
            "Permit(s) attached to this event have already been submitted to the OMHA.",
        )
        return redirect("events:exhibition-details", event_id=instance.id)

    form = NewExhibitionForm(request.POST or None, instance=instance)

    if request.method == "POST" and form.is_valid():

        if request.POST.get("delete"):
            instance.delete()
            return redirect("events:exhibitions-list")
        else:
            form.save()

        return redirect_next(
            request, resolve_url("events:exhibition-details", event_id=instance.id)
        )

    return render(
        request,
        "events/event_new.html",
        {
            "event_type": "exhibition",
            "form": form,
            "editing": True,
        },
    )
