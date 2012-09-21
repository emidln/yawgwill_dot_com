

def getvars(request):
    d = {'getvars': ''}
    getvars = request.GET.copy()
    if 'page' in getvars:
        del getvars['page']
    if len(getvars.keys()) > 0:
        d['getvars'] = getvars.urlencode()
    return d
