
from django.db.models import Q

from cards.models import *


def import_sets(sets):
    created = 0
    for s in sets:
        obj, was_created = Set.objects.get_or_create(code=s.code, name=s.name)
        if was_created:
            created += 1
    return created

def parse_type_line(line):
    results = line.split('-')
    first_split = results[0].split()
    card_type = first_split.pop()
    super_types = first_split
    sub_types = results[1].split()
    return super_types, card_type, sub_types

def create_CardType(supers, normal, subs):
    super_types = []
    for x in supers:
        super_types.append(SuperType.objects.get_or_create(name=x)[0])

    sub_types = []
    for x in subs:
        sub_types.append(SubType.objects.get_or_create(name=x)[0])

    q = Q(type=normal)
    q = q and Q(super_types__name__in=supers)
    q = q and Q(sub_types__name__in=subs)

    r = CardType.objects.filter(q)
    if r.count():
        return r[0]
    else:
        ct = CardType(type=normal)
        ct.super_types = super_types
        ct.sub_types = sub_types
        ct.save()
        return ct

def extract_abilities(text, type_hint=None):

    l = [
            'Deathtouch',
            'Defender',
            'Double Strike',
            'Enchant',
            'Equip',
            'First Strike',
            'Flash',
            'Flying',
            'Haste',
            'Hexproof',
            'Intimidate',
            'Islandwalk',
            'Swampwalk',
            'Plainswalk',
            'Forestwalk',
            'Mountainwalk',
            'Lifelink',
            'Protection',
            'Reach',
            'Shroud',
            'Trample',
            'Vigilence',
            'Banding',
            'Rampage',
    ]
    permanent_abilities_list = [
            'Exalted',
            'Indestructibe',
            'Shroud',
    ]

    spells_abilities_list = [
            'Cascade',
            'Delve',
            'Split Second',
    ]

    instant_sorcery_abilities_list = [
            'Storm',
            'Flashback',
    ]

    creature_abilities_list = [
        'Flying.',
        'First Strike.',
        'Fear',
        'Vigilance',
        'Delve',
    ]
    artifact_abilties_list = [
        'Cascade',
        'Shroud',
        'Indestructible,
    ]
    enchantment_abilities_list = [
        'Shroud',
    ]
    land_abilities_list = [
        'Indestructible',
        'Shroud',
    ]
    sorcery_abilities_list = [
        'Storm',
        'Cascade',
        'Flashback',
        'Delve',
    ]
    instant_abilities_list = [
        'Storm',
        'Cascade',
        'Flashback',
        'Delve',
    ]
    planeswalker_abilities_list = []

def import_cards(cards_filename):
    with open(cards_filename) as f:
        cards = json.load(f)

    for card in cards:
        colors = []
        for code in card['color']:
            colors.append(Color.objects.get_or_create(code=code)[0])

        sets = []
        for s in card['set']:
            current_set = Set.objects.get(s['text'])
            url = s['attrs']['picURL']
            sets.append((current_set, url))

        power, toughness = card['pt'].split('/')
        c = Card()
        c.card_type = create_CardType(*parse_type_line(card.type))
        c.power = power
        c.toughness = toughness
        c.save()
        for s in sets:
            CardSetImageURL.objects.create(set=s[0],url=s[1],card=c)


