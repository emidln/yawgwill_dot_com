import json
import string

from django.db.models import Q

from models import Set, Type, SuperType, SubType, CardType, Card, Color, CardSetImageURL

number_set = set(map(str, range(10)))
color_set = set('UBGRWP')


def check_builder(l, n):
    return {x: n for x in l}


CHECKER = check_builder(string.uppercase, 2)
CHECKER.update(check_builder(string.lowercase, 1))
CHECKER.update({' ': 0})
CHECKER.update(check_builder('.,!?:', 3))


def check(c):
    """ return 2 for uppercase, 1 for lowercase, 0 otherwise """
    return CHECKER.get(c, 4)


def reducer(x, y):
    """ Helper for recover spaces. If x is lowercase and y is uppercase, insert
        a space because we have a runon word to correct.
    """
    c0 = check(x[-1])
    c1 = check(y)
    # if either character is a space, no change
    if c0 == 0 or c1 == 0:
        return x + y
    elif c0 == 1:
        # lowercase -> lowercase = no change
        if c1 == 1:
            return x + y
        # lowercase -> uppercase = insert space
        elif c1 == 2:
            return x + ' ' + y
        # lowercase -> punctuation = no change
        elif c1 == 3:
            return x + y
        # lowercase -> other = insert space
        elif c1 == 4:
            return x + ' ' + y
        raise Exception('lowercase -> unhandled')
    elif c0 == 3:
        # punctuation -> non-space
        return x + ' ' + y
    elif c0 == 2:
        # uppercase -> anything, no change
        return x + y
    return x + y


def recover_spaces(sentence):
    """ Given a sentence where lines were joined by removing the newline, return
        add spaces where they might logically go.
    """
    return ' '.join(map(lambda word: reduce(reducer, word), sentence.split()))


def color(c):
    """ return color or C denoting colorless """
    if c in color_set:
        return c
    return 'C'


def cost(c):
    """ return the cmc of a character """
    try:
        return int(c)
    except ValueError:
        if c == 'X':
            return 0
        return 1


def handle_parens(partial_cost):
    """ handle what is inside a set of parenthesis """
    costs = []
    colors = set()

    number_tmp = None
    for i, c in enumerate(partial_cost):
        if c == '/':
            if number_tmp is not None:
                costs.append(cost(''.join(number_tmp)))
                colors.add('C')
                number_tmp = None
            continue
        if c == ')':
            if number_tmp is not None:
                costs.append(cost(''.join(number_tmp)))
                colors.add('C')
                number_tmp = None
            break
        if c in number_set:
            if number_tmp is not None:
                number_tmp.append(c)
            else:
                number_tmp = [c]
        else:
            # handle (10G/U) as a cost
            if number_tmp is not None:
                costs.append(cost(''.join(number_tmp)))
                colors.add('C')
                number_tmp = None
            costs.append(cost(c))
            colors.add(color(c))

    return partial_cost[i + 1:], max(costs), colors


def parse_manacost(mana_cost):
    """ parse the mana cost with help from handle_parens """
    current_index = 0
    current_source = mana_cost[:]
    current_length = len(current_source)

    total_cost = 0
    colors = set()

    # number_tmp lives as None when not in use
    number_tmp = None
    while current_index < current_length:
        char = current_source[current_index]
        if char == '(':
            # compact number tmp since we're done with numbers
            if number_tmp is not None:
                total_cost += cost(''.join(number_tmp))
                colors.add('C')
                number_tmp = None
            results = handle_parens(current_source[current_index + 1:])
            current_source = results[0]
            current_index = -1
            current_length = len(current_source)
            total_cost += results[1]
            colors = colors | results[2]
            if not current_source:
                break
        else:
            # if we have a number, utilize number_tmp
            if char in number_set:
                if number_tmp is not None:
                    number_tmp.append(char)
                else:
                    number_tmp = [char]
            else:
                # compact number_tmp since we're done with numbers
                if number_tmp is not None:
                    total_cost += cost(''.join(number_tmp))
                    colors.add('C')
                    number_tmp = None
                total_cost += cost(char)
                colors.add(color(char))
        current_index += 1
    else:
        if number_tmp is not None:
            total_cost += cost(''.join(number_tmp))
            colors.add('C')
            number_tmp = None

    if 'C' in colors:
        tmp = colors & color_set
        if tmp:
            colors = tmp

    return {'cost': total_cost, 'colors': colors}


def test_parse_manacost():
    mana_costs = {
            '1': 1,
            '0': 0,
            '15': 15,
            '8GG': 10,
            'X1RR': 3,
            '2(G/B)': 3,
            '(W/B)(W/B)(W/B)': 3,
            '(2/W)(2/W)(2/w)': 6,
    }
    for mc, cmc in mana_costs.iteritems():
        assert(parse_manacost(mc)['cost'] == cmc)
        print "okay"


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
        text = card['text']
        if text is not None:
            c.text = recover_spaces(card['text'])
        c.name = card['name']
        c.type = create_CardType(*parse_type_line(card['type']))
        c.power = power
        c.toughness = toughness
        c.cmc = cmc
        if manacost is not None:
            c.mana_cost = manacost
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
