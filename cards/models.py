from django.db import models


class Color(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=30, blank=True, null=True)

    def __unicode__(self):
        return self.code


class Type(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name


class SuperType(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name


class SubType(models.Model):
    name = models.CharField(max_length=45)

    def __unicode__(self):
        return self.name


class CardType(models.Model):
    type = models.ForeignKey(Type, related_name='card_types')
    sub_types = models.ManyToManyField(SubType, related_name='card_types')
    super_types = models.ManyToManyField(SuperType, related_name='card_types')

    def __unicode__(self):
        supers = [x.name.lower().title() for x in self.super_types.all()]
        subs = [x.name.lower().title() for x in self.sub_types.all()]
        name = self.type.name.lower().title()
        s = '%s'
        args = [name]
        if supers:
            s += ' %s'
            args.insert(0, ' '.join(sorted(supers)))
        if subs:
            s += ' - %s'
            args.append(' '.join(sorted(subs)))
        return s % tuple(args)


class Set(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=60)

    def __unicode__(self):
        return self.code


class CardSetImageURL(models.Model):
    url = models.URLField()
    card = models.ForeignKey('Card', related_name='set_images')
    set = models.ForeignKey(Set, related_name='card_images')

    def __unicode__(self):
        return self.url


#class Keyword(models.Model):
#    name = models.CharField(max_length=30)
#
#    def __unicode__(self):
#        return self.name


class Card(models.Model):
    name = models.CharField(max_length=128)
    text = models.CharField(max_length=1024, blank=True, null=True)
    mana_cost = models.CharField(max_length=20, blank=True, null=True)
    power = models.CharField(max_length=5, blank=True, null=True)
    toughness = models.CharField(max_length=5, blank=True, null=True)
    cmc = models.IntegerField(default=0)
    loyalty = models.IntegerField(blank=True,null=True)
    #keywords = models.ManyToManyField(Keyword, related_name='cards')
    sets = models.ManyToManyField(Set, through=CardSetImageURL)
    colors = models.ManyToManyField(Color, related_name='cards', blank=True, null=True)
    type = models.ForeignKey(CardType, related_name='cards')

    def __unicode__(self):
        return self.name
