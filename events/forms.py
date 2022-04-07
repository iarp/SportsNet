from django import forms
from django.utils import timezone

from events.models import Exhibition, Tournament


class NewTournamentForm(forms.ModelForm):
    required_css_class = "required"

    class Meta:
        model = Tournament
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "sanction_number": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "City, Province/State"}
            ),
            "start_date": forms.DateInput(
                attrs={"class": "datepicker form-control", "placeholder": "YYYY-MM-DD"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "datepicker form-control", "placeholder": "YYYY-MM-DD"}
            ),
            "association": forms.Select(attrs={"class": "form-control"}),
            "website": forms.TextInput(
                attrs={
                    "placeholder": "URL to webpage about tournament. Optional but recommended to supply"
                }
            ),
        }
        fields = (
            "name",
            "association",
            "association_other",
            "sanction_number",
            "location",
            "start_date",
            "end_date",
            "website",
        )

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            self.add_error("end_date", "End date cannot be before start date")

        return cleaned_data


class NewExhibitionForm(forms.ModelForm):
    required_css_class = "required"

    class Meta:
        model = Exhibition
        widgets = {
            "destination": forms.TextInput(attrs={"placeholder": "City, Province"}),
        }

        fields = (
            "other_team",
            "other_team_association",
            "other_team_association_other",
            "destination",
            "arena",
            "start_date",
            "end_datetime",
            "rink",
            "referee_requirements",
            "timekeeper_needed",
            "timekeeper_notes",
            "required_referee_or_timekeeper",
            "cell_phone",
            "contact_name",
        )

    start_date = forms.DateTimeField(
        input_formats=["%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M:%S"],
        widget=forms.DateTimeInput(
            attrs={"class": "datepicker", "placeholder": "YYYY-MM-DD HH:MM AM/PM"}
        ),
    )

    end_datetime = forms.DateTimeField(
        input_formats=["%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M:%S"],
        widget=forms.DateTimeInput(
            attrs={"class": "datepicker", "placeholder": "YYYY-MM-DD HH:MM AM/PM"}
        ),
    )

    req_ack = forms.BooleanField(required=False)

    def clean_end_datetime(self):
        try:
            start = self.cleaned_data["start_date"]
            end = self.cleaned_data["end_datetime"]
            return timezone.make_aware(
                timezone.datetime(
                    year=start.year,
                    month=start.month,
                    day=start.day,
                    hour=end.hour,
                    minute=end.minute,
                    second=end.second,
                )
            )
        except:
            raise forms.ValidationError("System Error, try again or contact the office")

    def clean(self):

        cleaned_data = super(NewExhibitionForm, self).clean()

        try:
            start = self.cleaned_data["start_date"]
            end = self.cleaned_data["end_datetime"]

            diff = end - start
            diff = divmod(diff.days * 86400 + diff.seconds, 60)[0]

            if diff <= 30:
                self.add_error(
                    "end_datetime",
                    f"Exhibition is too short at {diff} minutes, "
                    f"it must be longer than 30 minutes",
                )
        except:
            pass

        if cleaned_data.get("required_referee_or_timekeeper"):

            if not cleaned_data.get("referee_requirements"):
                self.add_error(
                    "referee_requirements",
                    "Referee Requirements required if requesting officials.",
                )

            if not cleaned_data.get("req_ack"):
                self.add_error("req_ack", "You must accept this acknowledgement")

            if not cleaned_data.get("cell_phone"):
                self.add_error(
                    "cell_phone",
                    "A Cell Phone number is required in case something comes up",
                )

        return cleaned_data
