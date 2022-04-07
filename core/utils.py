from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls.exceptions import NoReverseMatch


def redirect_next(request, default):
    """Redirects to a given page, except if the session has a next value given.

    Args:
        request: WSGIRequest object
        default: Default location to go to if no next is given.

    Returns:
        HttpResponseRedirect
    """
    if request:
        if request.session.get("next"):
            default = request.session["next"]
            del request.session["next"]
        elif request.GET.get("next"):
            default = request.GET.get("next")
        elif request.POST.get("next"):
            default = request.POST.get("next")

    try:
        return redirect(default)
    except NoReverseMatch:
        return HttpResponseRedirect(default)
