import json

from django.db.models import Q

from models import Set, Type, SuperType, SubType, CardType, Card, Color, CardSetImageURL


def calculate_cmc(mana_cost):
    return parse_manacost(mana_cost)['cost']


def calculate_colors(mana_cost):
    return parse_manacost(mana_cost)['colors']


def parse_manacost(manacost):
    if manacost is None:
        return {'cost': 0, 'colors': set()}
    cost = 0
    colors = set()
    inside = False
    for c in list(manacost):
        try:
            i = int(c)
            cost += i
        except ValueError:
            if c == '(':
                inside = True
                continue
            if inside:
                if c == ')':
                    cost += 1
                    inside = False
                    continue
                if c == '/':
                    continue
            else:
                cost += 1
            colors.add(c)
    return {'cost': cost, 'colors': colors}


def import_sets(sets):
    created = 0
    for code, name in sets.iteritems():
        obj, was_created = Set.objects.get_or_create(code=code, name=name)
        if was_created:
            created += 1
    return created


def parse_type_line(line):
    results = line.split('-')
    first_split = results[0].split()
    card_type = first_split.pop()
    super_types = first_split
    sub_types = []
    if len(results) > 1:
        sub_types = results[1].split()
    return super_types, card_type, sub_types


def create_CardType(supers, normal, subs):
    super_types = []
    for x in supers:
        super_types.append(SuperType.objects.get_or_create(name=x)[0])

    sub_types = []
    for x in subs:
        sub_types.append(SubType.objects.get_or_create(name=x)[0])

    normal_type = Type.objects.get_or_create(name=normal)[0]

    q = Q(type=normal_type)
    q = q and Q(super_types__name__in=supers)
    q = q and Q(sub_types__name__in=subs)

    r = CardType.objects.filter(q)
    if r.count():
        return r[0]
    else:
        ct = CardType(type=normal_type)
        ct.save()
        ct.super_types = super_types
        ct.sub_types = sub_types
        ct.save()
        return ct


def import_cards(cards_filename):
    with open(cards_filename) as f:
        cards = json.load(f)

    for card in cards:

        colors = []
        cmc = 0
        manacost = card.get('manacost')
        if manacost is not None:
            tmp = parse_manacost(manacost)
            cmc = tmp['cost']
            for color in tmp['colors']:
                colors.append(Color.objects.get_or_create(code=color)[0])

        sets = []
        card_set = card['set']
        if not isinstance(card_set, list):
            card_set = [card_set]

        for s in card_set:
            current_set = Set.objects.get(code=s['text'])
            url = s['attrs']['picURL']
            sets.append((current_set, url))

        power = None
        toughness = None
        pt = card.get('pt')
        if pt:
            power, toughness = pt.split('/')
        c = Card()
        c.name = card['name']
        c.type = create_CardType(*parse_type_line(card['type']))
        c.power = power
        c.toughness = toughness
        c.cmc = cmc
        c.loyalty = card.get('loyalty')
        c.save()
        c.colors = colors
        for s in sets:
            CardSetImageURL.objects.create(set=s[0], url=s[1], card=c)

        #print c.name, c.type, c.power, c.toughness, c.cmc, c.colors.all(), colors, c.sets.all()


def import_sets_json(sets_filename):
    with open(sets_filename) as f:
        sets = json.load(f)

    return import_sets(sets)
