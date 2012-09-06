new_cards_doc = []
for x in cards.iterchildren():
    c = defaultdict(list)
    for element in card.iterchildren():
        i = element.items()
        if len(i):
            d = dict(i)
            c[element.tag] = {'text': element.text, 'attrs': d}
        else:
            c[element.tag].append(element.text)
    for k,v in c.iteritems():
        if isinstance(v, list):
            if len(v) == 1:
                c[k] = v[0]
    c = dict(c)
    new_cards_doc.append(c)
