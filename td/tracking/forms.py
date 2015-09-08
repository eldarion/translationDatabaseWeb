from django import forms
from django.core.urlresolvers import reverse as urlReverse
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import gettext as _
# from django.utils.formats import mark_safe
# from django.utils import timezone

from td.models import Country, Language
from .models import Charter, Department, Event

import re


class MySelectDateWidget(SelectDateWidget):

    # Put Required=True on hold so the widget will include empty_label upon render
    def create_select(self, *args, **kwargs):
        old_state = self.is_required
        self.is_required = False
        result = super(MySelectDateWidget, self).create_select(*args, **kwargs)
        self.is_required = old_state
        return result

class CharterForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CharterForm, self).__init__(*args, **kwargs)
        self.fields['countries'].queryset = Country.objects.order_by('name')
        self.fields['lead_dept'].queryset = Department.objects.order_by('name')
        self.fields['language'] = forms.CharField(
            widget = forms.TextInput(
                attrs = {
                    "class": "language-selector",
                    "data-source-url": urlReverse("names_autocomplete")
                }
            ),
            required = True
        )

        # Checking what?
        # Something to do with trying to create a duplicate charter.
        # Form says "undefined" if this is commented out.
        if self.instance.pk:
            lang = self.instance.language
            if lang:
                self.fields["language"].widget.attrs["data-lang-pk"] = lang.id
                self.fields["language"].widget.attrs["data-lang-ln"] = lang.ln
                self.fields["language"].widget.attrs["data-lang-lc"] = lang.lc
                self.fields["language"].widget.attrs["data-lang-lr"] = lang.lr
                self.fields["language"].widget.attrs["data-lang-gl"] = lang.gateway_flag
        elif self.data.get("language", None):
            try:
                lang = Language.objects.get(pk=self.data["language"])
                self.fields["language"].widget.attrs["data-lang-pk"] = lang.id
                self.fields["language"].widget.attrs["data-lang-ln"] = lang.ln
                self.fields["language"].widget.attrs["data-lang-lc"] = lang.lc
                self.fields["language"].widget.attrs["data-lang-lr"] = lang.lr
                self.fields["language"].widget.attrs["data-lang-gl"] = lang.gateway_flag
            except:
                pass

    # def clean_number(self):
        # Validate the format of project (accounting) number

    # Since a name can have unexpected characters, only check against empty
    def clean_contact_person(self):
        name = self.cleaned_data['contact_person']
        name = name.strip()
        if not name:
            raise forms.ValidationError(_('This field is required'), 'invalid_input')
        else:
            return name

    class Meta:
        model = Charter
        exclude = ['created_at']
        widgets = {
            'created_by': forms.HiddenInput(),
            'start_date': SelectDateWidget(
                attrs={'class': 'date-input'}
            ),
            'end_date': MySelectDateWidget(
                attrs = {'class': 'date-input'}
            ),
        }
        


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'charter',
            'location',
            'start_date',
            'end_date',
            'lead_dept',
            'materials',
            'translators',
            'facilitators',
            'output_target',
            'translation_method',
            'tech_used',
            'comp_tech_used',
            'networks',
            'departments',
            'pub_process',
            'follow_up'
        ]