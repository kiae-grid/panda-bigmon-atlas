
from os.path import dirname, join
import sys

import core
import atlas


## Inherit some variables from the core module if they are
## not defined in our configuration.  Inject them to the
## namespace to allow for usual "from .local import XXX".

inherit_vars = ('MY_SECRET_KEY', 'dbaccess', 'LOG_ROOT', 'defaultDatetimeFormat')
__local_module = ".".join(__name__.split(".")[0:-1] + ["local"])
__core_module = sys.modules["core.common.settings"]
try:
    __module = __import__(__local_module, globals(), locals(), inherit_vars, -1)
except ImportError, e:
    # Django usually catches exception and prints not so meaningful
    # traceback, so provide our own one too.
    import traceback
    print("Error importing module %s: %s" % (__local_module, e))
    traceback.print_tb(sys.exc_traceback, None)
    raise e
for name in inherit_vars:
    try:
        getattr(__module, name)
    except AttributeError:
        setattr(__module, name, getattr(__core_module, name))


from .local import MY_SECRET_KEY, dbaccess

ALLOWED_HOSTS = [
    ### cern.ch
    '.cern.ch',  # Allow domain and subdomains
    '.cern.ch.',  # Also allow FQDN and subdomains
    ### bigpanda.cern.ch
    'bigpanda.cern.ch',  # Allow domain and subdomains
    'bigpanda.cern.ch.',  # Also allow FQDN and subdomains
    ### pandawms.org
    '.pandawms.org',  # Allow domain and subdomains
    '.pandawms.org.',  # Also allow FQDN and subdomains
]


### VIRTUALENV
#VIRTUALENV_PATH = '/data/virtualenv/django1.6.1__python2.6.6__jedimon'
VIRTUALENV_PATH = '/data/virtualenv/django1.6.1__python2.6.6__atlas'

### WSGI
WSGI_PATH = VIRTUALENV_PATH + '/pythonpath'

DATABASE_ROUTERS = ['atlas.dbrouter.ProdMonDBRouter']

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(dirname(core.common.__file__), 'static'),
#    join(join(dirname(core.__file__),'datatables'), 'static'),
#    join(dirname(atlas.__file__), 'static'),
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(dirname(core.common.__file__), 'templates'),
    join(dirname(atlas.__file__), 'templates'),
)

STATIC_ROOT = join(dirname(atlas.__file__), 'static')
#STATIC_ROOT = None
MEDIA_ROOT = join(dirname(atlas.__file__), 'media')
STATIC_URL_BASE = '/static/'
#STATIC_URL_BASE = '/jedimonstatic/'
MEDIA_URL_BASE = '/media/'
#MEDIA_URL_BASE = '/jedimonmedia/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = MY_SECRET_KEY

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = dbaccess

### URL_PATH_PREFIX for multi-developer apache/wsgi instance
### on EC2: URL_PATH_PREFIX = '/bigpandamon' or URL_PATH_PREFIX = '/developersprefix'
#URL_PATH_PREFIX = '/atlas'
#URL_PATH_PREFIX = '/jedimon'
URL_PATH_PREFIX = ''
### on localhost:8000: URL_PATH_PREFIX = '/.'
#URL_PATH_PREFIX = ''
MEDIA_URL = URL_PATH_PREFIX + MEDIA_URL_BASE
STATIC_URL = URL_PATH_PREFIX + STATIC_URL_BASE


## init logger
## A sample logging configuration. The only tangible logging
## performed by this configuration is to send an email to
## the site admins on every HTTP 500 error when DEBUG=False.
## See http://docs.djangoproject.com/en/dev/topics/logging for
## more details on how to customize your logging configuration.
from .logconfig import LOGGING


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'shibsso.middleware.ShibSSOMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)


AUTHENTICATION_BACKENDS = (
#    'atlas.auth.fake.backends.LoginAsBackend',
    'atlas.auth.voms.backends.VomsBackend',
    'shibsso.backends.ShibSSOBackend',
)


# Settings for authentication variables

SHIB_SSO_ADMIN = True
SHIB_SSO_CREATE_ACTIVE = True
SHIB_SSO_CREATE_STAFF = False
SHIB_SSO_CREATE_SUPERUSER = False
SHIB_LOGIN_PATH = '/Shibboleth.sso/?target='
SHIB_LOGOUT_URL = 'https://login.cern.ch/adfs/ls/?wa=wsignout1.0&returnurl='
META_EMAIL = 'ADFS_EMAIL'
META_FIRSTNAME = 'ADFS_FIRSTNAME'
META_GROUP = 'ADFS_GROUP'
META_LASTNAME = 'ADFS_LASTNAME'
META_USERNAME = 'ADFS_LOGIN'
LOGIN_REDIRECT_URL = '/'

#FAKE_LOGIN_AS_USER = 'username'
