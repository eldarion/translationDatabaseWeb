from collections import defaultdict

from django.db import models
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.models import ContentType
from jsonfield import JSONField

from model_utils import FieldTracker


@python_2_unicode_compatible
class Network(models.Model):
    name = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("network_detail", args=[self.pk])

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Region(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)
    tracker = FieldTracker()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


@python_2_unicode_compatible
class Country(models.Model):
    code = models.CharField(max_length=2, unique=True)
    alpha_3_code = models.CharField(max_length=3, blank=True, default="")
    name = models.CharField(max_length=75)
    region = models.ForeignKey(Region, null=True, blank=True, related_name="countries")
    population = models.IntegerField(null=True, blank=True)
    primary_networks = models.ManyToManyField(Network, blank=True)
    extra_data = JSONField(blank=True)

    tracker = FieldTracker()

    def gateway_language(self):
        if not hasattr(self, "_gateway_language"):
            data = self.extra_data
            if not isinstance(data, dict):
                data = {}
            self._gateway_language = next(iter(Language.objects.filter(code=data.get("gateway_language"))), None)
        return self._gateway_language

    def gateway_languages(self, with_primary=True):
        gl = self.gateway_language()
        if gl:
            ogls = [gl]
        else:
            ogls = []
        for lang in self.language_set.all():
            if lang.gateway_flag and lang not in ogls:
                ogls.append(lang)
            elif lang.gateway_language and lang.gateway_language not in ogls:
                ogls.append(lang.gateway_language)
        if not with_primary and gl:
            ogls.remove(gl)
        return ogls

    @classmethod
    def regions(cls):
        qs = cls.objects.all().values_list("region", flat=True).distinct()
        qs = qs.order_by("region.name")
        return qs

    @classmethod
    def gateway_data(cls):
        with_gateways = cls.objects.filter(language__gateway_language__isnull=False).distinct()
        without_gateways = cls.objects.exclude(pk__in=with_gateways)
        data = {
            x.code: {"obj": x, "gateways": defaultdict(lambda: [])}
            for x in with_gateways
        }
        data.update({
            x.code: {"obj": x, "gateways": {"n/a": list(x.language_set.all())}}
            for x in without_gateways
        })
        for country in with_gateways:
            for lang in country.language_set.all():
                if lang.gateway_language:
                    data[country.code]["gateways"][lang.gateway_language.code].append(lang)
                else:
                    data[country.code]["gateways"]["n/a"].append(lang)
        return data

    def __str__(self):
        return self.name


def transform_country_data(data):
    tree = {"name": "World", "parent": None, "children": []}
    for code in data:
        datum = {
            "name": data[code]["obj"].name,
            "parent": "World",
            "children": [],
            "hasGatewayLanguages": len(data[code]["gateways"]) > 1,
            "detailUrl": reverse("country_detail", args=[data[code]["obj"].pk])
        }
        for gateway in data[code]["gateways"]:
            if gateway == "n/a":
                name = "No Gateway"
            else:
                name = data[code]["gateways"][gateway][0].gateway_language.name
            gdatum = {
                "name": name,
                "parent": data[code]["obj"].name,
                "children": [
                    {
                        "name": l.name,
                        "detailUrl": reverse("language_detail", args=[l.pk]),
                        "parent": name,
                        "children": []
                    }
                    for l in data[code]["gateways"][gateway]
                ],
                "notGatewayLanguage": gateway == "n/a"
            }
            datum["children"].append(gdatum)
        tree["children"].append(datum)
    return tree

"""
tree = {
    "name": "Root",
    "parent": None,
    "children": [
        {"name": "", "parent": "Root", "children": []},
        {"name": "", "parent": "Root", "children": []},
        {"name": "", "parent": "Root", "children": []},
    ]
}
"""


@python_2_unicode_compatible
class Language(models.Model):
    DIRECTION_CHOICES = (
        ("l", "ltr"),
        ("r", "rtl")
    )
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    gateway_language = models.ForeignKey("self", related_name="gateway_to", null=True, blank=True)
    native_speakers = models.IntegerField(null=True, blank=True)
    networks_translating = models.ManyToManyField(Network, blank=True)
    gateway_flag = models.BooleanField(default=False, blank=True, db_index=True)
    direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES, default="l")
    iso_639_3 = models.CharField(max_length=3, default="", db_index=True, blank=True, verbose_name="ISO-639-3")
    extra_data = JSONField(blank=True)

    tracker = FieldTracker()

    def __str__(self):
        return self.name

    @property
    def cc(self):
        if self.country:
            return self.country.code.encode("utf-8")
        return ""

    @property
    def lr(self):
        if self.country and self.country.region:
            return self.country.region.name.encode("utf-8")
        return ""

    @property
    def lc(self):
        return self.code

    @property
    def ln(self):
        return self.name.encode("utf-8")

    @classmethod
    def codes_text(cls):
        return " ".join([
            x.code
            for x in cls.objects.all().order_by("code")
        ])

    @classmethod
    def names_text(cls):
        return "\n".join([
            "{}\t{}".format(x.code, x.name.encode("utf-8"))
            for x in cls.objects.all().order_by("code")
        ])

    @classmethod
    def names_data(cls):
        return [
            dict(pk=x.pk, lc=x.lc, ln=x.ln, cc=[x.cc], lr=x.lr, gw=x.gateway_flag, ld=x.get_direction_display())
            for x in cls.objects.all().order_by("code")
        ]


@python_2_unicode_compatible
class Media(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Media"


@python_2_unicode_compatible
class Publisher(models.Model):
    name = models.CharField(max_length=255)
    extra_data = JSONField(blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Title(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    publisher = models.ForeignKey(Publisher, blank=True, null=True)
    extra_data = JSONField(blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Resource(models.Model):
    title = models.ForeignKey(Title, related_name="versions")
    language = models.ForeignKey(Language, related_name="resources")
    medias = models.ManyToManyField(Media, blank=True, verbose_name="Media")
    publisher = models.ForeignKey(Publisher, blank=True, null=True)
    published_flag = models.BooleanField(default=True, db_index=True, blank=True)
    published_date = models.DateField(default=None, null=True, blank=True, db_index=True)
    copyright_year = models.IntegerField(default=None, null=True, blank=True, db_index=True, verbose_name="copyright")
    extra_data = JSONField(blank=True)

    def the_publisher(self):
        return self.publisher or self.title.publisher

    def __str__(self):
        return "{0} in {1}".format(str(self.title), str(self.language))

    class Meta:
        unique_together = ("title", "language")


class EAVBase(models.Model):
    attribute = models.CharField(max_length=100)
    value = models.CharField(max_length=250)
    source_ct = models.ForeignKey(ContentType)
    source_id = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class CountryEAV(EAVBase):
    entity = models.ForeignKey(Country, related_name="attributes")


class LanguageEAV(EAVBase):
    entity = models.ForeignKey(Language, related_name="attributes")
