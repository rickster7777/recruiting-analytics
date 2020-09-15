from django.db import models

# Create your models here.


class ProspectsPersonality(models.Model):
    team_player = models.IntegerField(null=True, blank=True)
    coachability = models.IntegerField(null=True, blank=True)
    openness = models.IntegerField(null=True, blank=True)
    extroverted = models.IntegerField(null=True, blank=True)
    temperament = models.IntegerField(null=True, blank=True)


class ProspectsNeeds(models.Model):
    challenge = models.IntegerField(null=True, blank=True)
    structure = models.IntegerField(null=True, blank=True)
    stability = models.IntegerField(null=True, blank=True)
    excitement = models.IntegerField(null=True, blank=True)
    ideal = models.IntegerField(null=True, blank=True)


class ProspectsValues(models.Model):
    tradition = models.IntegerField(null=True, blank=True)
    stimulation = models.IntegerField(null=True, blank=True)
    helping_others = models.IntegerField(null=True, blank=True)
    achievement = models.IntegerField(null=True, blank=True)
    taking_pleasure_in_life = models.IntegerField(null=True, blank=True)


class PersonalityInsights(models.Model):
    personality = models.ForeignKey(
        ProspectsPersonality,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    needs = models.ForeignKey(
        ProspectsNeeds,
        blank=True,
        null=True,
        on_delete=models.SET_NULL

    )
    values = models.ForeignKey(
        ProspectsValues,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
