from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from accounts.forms import AccountSettingsForm


@login_required
def account_settings(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AccountSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Préférences mises à jour."))
            return redirect("accounts:settings")
    else:
        form = AccountSettingsForm(instance=request.user)
    return render(request, "accounts/settings.html", {"form": form})
