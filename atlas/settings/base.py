
from os.path import dirname, join

import core
from core import common
from core.common.settings.base import COMMON_INSTALLED_APPS
import atlas
import atlas.todoview as atlas_todoview


VERSIONS = {
    'core': core.__versionstr__,
    'atlas': atlas.__versionstr__,
}


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(dirname(atlas.__file__), 'templates'),
    join(dirname(atlas_todoview.__file__), 'templates'),
    join(dirname(common.__file__), 'templates'),
)

INSTALLED_APPS_BIGPANDAMON_ATLAS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'atlas.auth.voms',

    ### BigPanDAmon core
    'core.common',
    'core.table',
#    'core.graphics', #NOT-IMPLEMENTED
    'core.pandajob',
    'core.resource',
#    'core.htcondor', #NOT-NEEDED-IN-ATLAS
    'core.datatables',
#    'core.gspread', #NOT-NEEDED-IN-ATLAS?
    'atlas.prodtask',
    ### atlas.todoview: Placeholder for views which need to be implemented
    ### as part of cross-linking between jobs and tasks monitoring
    'atlas.todoview',
    'atlas.getdatasets', 
    'django_tables2',#pip install django_tables2
)
INSTALLED_APPS = COMMON_INSTALLED_APPS + INSTALLED_APPS_BIGPANDAMON_ATLAS
JS_I18N_APPS_EXCLUDE = common.settings.base.JS_I18N_APPS_EXCLUDE + ('django_tables2',)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request', #django-tables2
)


ROOT_URLCONF = 'atlas.urls'

SITE_ID = 2

# email
EMAIL_SUBJECT_PREFIX = 'bigpandamon-atlas: '


