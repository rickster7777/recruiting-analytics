from django.db import models

# Create your models here.


class Country(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)


class Region(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return str(self.name) if self.name else ''


class State(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    abbreviation = models.CharField(max_length=250, null=True, blank=True)
    region = models.ForeignKey(Region,
                               blank=True,
                               null=True,
                               on_delete=models.SET_NULL
                               )
    country = models.ForeignKey(Country,
                                blank=True,
                                null=True,
                                on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.name) if self.name else ''


class City(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    state = models.ForeignKey(State,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL
                              )

    def __str__(self):
        return str(self.name) if self.name else ''


class Address(models.Model):
    street_line_1 = models.CharField(max_length=450, null=True, blank=True)
    street_line_2 = models.CharField(max_length=450, null=True, blank=True)
    city = models.ForeignKey(City,
                             blank=True,
                             null=True,
                             on_delete=models.SET_NULL)
    state = models.ForeignKey(State,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return str(self.street_line_1) if self.street_line_1 else ''


class School(models.Model):
    name = models.CharField(max_length=450, null=True, blank=True)
    logo = models.FileField(blank=True, null=True, upload_to='schools-input/')
    address = models.ForeignKey(Address,
                                blank=True,
                                null=True,
                                on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.name) if self.name else ''


class College(models.Model):
    name = models.CharField(max_length=450, null=True, blank=True)
    city = models.ForeignKey(City,
                             blank=True,
                             null=True,
                             on_delete=models.SET_NULL)
    state = models.ForeignKey(State,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL)
    address = models.ForeignKey(Address,
                                blank=True,
                                null=True,
                                on_delete=models.SET_NULL)
    # logo = models.FileField(blank=True, null=True, upload_to='college-input/')

    def __str__(self):
        return str(self.name) if self.name else ''
