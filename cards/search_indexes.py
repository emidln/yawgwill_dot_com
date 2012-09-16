
from haystack import indexes
from models import *

class CardIndex(indexes.SearchIndex, indexes.Indexable):
    document = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    text = indexes.CharField(model_attr='text', null=True)
    loyalty = indexes.IntegerField(model_attr='loyalty', null=True, faceted=True)
    mana_cost = indexes.CharField(model_attr='mana_cost', null=True, faceted=True)
    power = indexes.CharField(model_attr='power', null=True, faceted=True)
    toughness = indexes.CharField(model_attr='toughness', null=True, faceted=True)
    cmc = indexes.IntegerField(model_attr='cmc', faceted=True)
    sets = indexes.MultiValueField(faceted=True)
    colors = indexes.MultiValueField(faceted=True)
    card_type = indexes.CharField(faceted=True)
    type = indexes.CharField(faceted=True)
    sub_types = indexes.MultiValueField(faceted=True)
    super_types = indexes.MultiValueField(faceted=True)

    def get_model(self):
        return Card

    def prepare_card_type(self, obj):
        return str(obj.type)

    def prepare_type(self, obj):
        return obj.type.type.name

    def prepare_sub_types(self, obj):
        return [x.name for x in obj.type.sub_types.all()]

    def prepare_super_types(self, obj):
        return [x.name for x in obj.type.super_types.all()]

    def prepare_colors(self, obj):
        return [c.code for c in obj.colors.all()]

    def prepare_sets(self, obj):
        return [x.code for x in obj.sets.all()]
