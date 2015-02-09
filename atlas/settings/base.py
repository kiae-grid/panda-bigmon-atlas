
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
)
INSTALLED_APPS = ('django_cassandra_engine',) + COMMON_INSTALLED_APPS + INSTALLED_APPS_BIGPANDAMON_ATLAS


ROOT_URLCONF = 'atlas.urls'

SITE_ID = 2

# email
EMAIL_SUBJECT_PREFIX = 'bigpandamon-atlas: '


