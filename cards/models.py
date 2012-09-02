from django.db import models

class Colors(model.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.code

def calculate_cmc(mana_cost):
    i = 0
    for x in list(mana_cost):
        try:
            i += int(x)
        except ValueError:
            i += 1
    return i

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
    sub_types = models.ManyToMany(SubType, related_name='card_types')
    super_types = models.ManyToMany(SuperType, related_name='card_types')

    def __unicode__(self):
        supers = [x.name.lower().title() for x in self.super_types.all()]
        subs = [x.name.lower().title() for x in self.sub_types.all()]
        name = self.type.lower().title()
        return '%s %s - %s' % (' '.join(sorted(supers)), name, ' '.join(sorted(subs)))

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

class Keyword(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

class Card(models.Model):
    name = models.CharField(max_length=128)
    text = models.CharField(max_length=1024)
    mana_cost = models.CharField(max_length=20)
    power = models.CharField(max_length=5)
    toughness = models.CharField(max_length=5)

    keywords = models.ManyToManyField(Keyword, related_name='cards')
    sets = models.ManyToManyField(Set, through=CardSetImageURL)
    colors = models.ManyToManyField(Color, related_name='cards')
    type = models.ForeignKey(CardType, related_name='cards')


    def cmc(self):
        return calculate_cmc(self.mana_cost)


