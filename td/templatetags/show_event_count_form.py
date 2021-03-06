from django.core.urlresolvers import reverse
from django.template.defaulttags import register

from td.models import WARegion, Country, Language
from td.utils import get_wa_fy


@register.inclusion_tag("tracking/_event_count_form.html", takes_context=True)
def show_event_count_form(context, **kwargs):

    mode = kwargs.get("mode") or (
        "language" if "language" in context
        else "country" if "country" in context
        else "region" if "wa_region" in context
        else "dashboard"
    )

    if mode == "region":
        default = context["wa_region"].slug if context.get("wa_region") else None
        selected_option = kwargs.get("selected_option", default)
        options = [(r.slug, r.name) for r in WARegion.objects.filter(slug__iexact=selected_option)]
    elif mode == "country":
        default = context["country"].code if context.get("country") else None
        selected_option = kwargs.get("selected_option", default)
        options = [(c.code, c.name) for c in Country.objects.filter(code__iexact=selected_option)]
    elif mode == "language":
        default = context["language"].code if context.get("language") else None
        selected_option = kwargs.get("selected_option", default)
        options = [(l.code, l.name) for l in Language.objects.filter(code__iexact=selected_option)]
    else:
        selected_option = kwargs.get("selected_option", None)
        options = [(r.slug, r.name) for r in WARegion.objects.all()]

    year = int(get_wa_fy().get("full_year"))

    selected_fy = kwargs.get("selected_fy", "0")
    fiscal_years = [(str(x), str(year + x)) for x in range(-4, 2)]

    container = kwargs.get("container", "")
    # If "container" is not specified, then the assumption is that this form is displayed on a page that has no
    # table for the event count and implies that this form will have have to be submitted to another page that does. The
    # default page to display the event count table is the Event Count page.
    form_action = kwargs.get("form_action", reverse("tracking:event_count")) if not container else ""

    return {"mode": mode, "selected_option": selected_option, "selected_fy": selected_fy, "form_action": form_action,
            "options": options, "fiscal_years": fiscal_years, "container": container}
