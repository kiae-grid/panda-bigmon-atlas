from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:

    url(r'^syncButton/(?P<rid>\d+)/$', 'atlas.prodtask.views.syncButton', name='syncButton'),

    url(r'^step_template_table/$', 'atlas.prodtask.views.step_template_table', name='step_template_table'),

    url(r'^step_execution_table/$', 'atlas.prodtask.views.step_execution_table', name='step_execution_table'),
    url(r'^stepex/(?P<rid>\d+)/$', 'atlas.prodtask.views.stepex_details', name='step_execution'),
    url(r'^inputlist_with_request/(?P<rid>\d+)/$', 'atlas.prodtask.views.input_list_approve', name='input_list_approve'),
    #url(r'^taskpriority_table/$', 'task.views.taskpriority_table', name='taskpriority_table'),

    url(r'^request_table/$',                'atlas.prodtask.request_views.request_table',   name='request_table'),
    url(r'^request/(?P<rid>\d+)/$',         'atlas.prodtask.request_views.request_details', name='request'),
    url(r'^request_clone/(?P<rid>\d+)/$',   'atlas.prodtask.request_views.request_clone',   name='request_clone'),
    url(r'^request_update/(?P<rid>\d+)/$',  'atlas.prodtask.request_views.request_update',  name='request_update'),
    url(r'^request_create/$',               'atlas.prodtask.request_views.request_create',  name='request_create'),

    url(r'^task_table/$',               'atlas.prodtask.task_views.task_table',         name='task_table'),
    url(r'^task/(?P<rid>\d+)/$',        'atlas.prodtask.task_views.task_details',       name='task'),
    url(r'^task_clone/(?P<rid>\d+)/$',  'atlas.prodtask.task_views.task_clone',         name='task_clone'),
    url(r'^task_update/(?P<rid>\d+)/$', 'atlas.prodtask.task_views.task_update',        name='task_update'),
    url(r'^task_create/$',              'atlas.prodtask.task_views.task_create',        name='task_create'),

    url(r'^step_approve/(?P<stepexid>\d+)/(?P<reqid>\d+)/(?P<sliceid>\d+)/$', 'atlas.prodtask.views.step_approve', name='step_approve'),

    url(r'^task_about/$', 'atlas.prodtask.views.about', name='about'),
    url(r'^$', 'atlas.prodtask.views.home', name='home'),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
)