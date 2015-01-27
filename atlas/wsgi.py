"""
WSGI config for bigpandamon project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/

further doc: http://thecodeship.com/deployment/deploy-django-apache-virtualenv-and-mod_wsgi/

"""

import os
import sys
import site
from os.path import join, pardir, abspath, dirname, split


virtualenvPath = None
try:
    from settings_bigpandamon_atlas import VIRTUALENV_PATH
    virtualenvPath = VIRTUALENV_PATH
except Exception, e:
    print "Export of VIRTUALENV_PATH from settings failed: %s" % (e)
    print "Can't work without virtualenv, exiting."
    sys.exit(1)
# Add the site-packages of the chosen virtualenv to work with
site.addsitedir(virtualenvPath + '/lib/python%s/site-packages' % \
  (".".join(map(lambda x: str(x), sys.version_info[0:2]))))


wsgi_path = None
try:
    from settings_bigpandamon_atlas import WSGI_PATH
    wsgi_path = WSGI_PATH
except Exception, e:
    print "Export of WSGI_PATH from settings failed: %s" % (e)
    print "Will not extend Python path."

if wsgi_path:
    sys.path.extend(wsgi_path.split(':'))


# django settings module
DJANGO_SETTINGS_MODULE = '%s.%s' % (split(abspath(dirname(__file__)))[1], 'settings')
os.environ['DJANGO_SETTINGS_MODULE'] = DJANGO_SETTINGS_MODULE


# pythonpath dirs
PYTHONPATH = [
    join(dirname(__file__), pardir), "/data/pandamon/maria/settings:/data/pandamon/maria/src/shibsso:/data/pandamon/maria/src/panda-bigmon-core:/data/pandamon/maria/src/panda-bigmon-atlas"
]

# inject few paths to pythonpath
for p in PYTHONPATH:
    if p not in sys.path:
        sys.path.insert(0, p)


# Activate virtual env
activate_env = os.path.expanduser(virtualenvPath + '/bin/activate_this.py')
execfile(activate_env, dict(__file__=activate_env))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
