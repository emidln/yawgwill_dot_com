# Yawgwill.com: Magic Search Project

Requirements
-------------
* some sort of \*nix (Linux, OSX, BSD)
* python 2.7
* elasticsearch


Instructions
-------------
To get started, you need to do the following:

    $ virtualenv env
    $ source env/bin/activate
    $ pip install -r pip-requirements.txt
    $ python manage.py syncdb --noinput
    $ python manage.py shell
    >>> from cards.utils import *
    >>> import_sets_json('sets.json')
    >>> import_cards('cards.json')
    >>> exit
    $ python manage.py rebuild_index
    y
    $ python manage.py collectstatic
    yes
    $ python manage.py runserver
    (starts a server on localhost:8000)

Loading the initial data should be built into a management command but I'm lazy.
