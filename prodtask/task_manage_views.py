
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import Context, Template, RequestContext
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

import core.datatables as datatables

from .forms import ProductionTaskForm, ProductionTaskCreateCloneForm, ProductionTaskUpdateForm
from .models import ProductionTask, TRequest, StepExecution

from .task_views import ProductionTaskTable, get_clouds, get_sites

from .task_actions import kill_task, finish_task, obsolete_task, change_task_priority, reassign_task_to_site, reassign_task_to_cloud

import json


_task_actions = {
    'kill': kill_task,
    'finish': finish_task,
    'obsolete': obsolete_task,
    'change_priority': change_task_priority,
    'reassign_to_site': reassign_task_to_site,
    'reassign_to_cloud': reassign_task_to_cloud,
}


def do_tasks_action(tasks, action, *args):

    if (not tasks) or not (action in _task_actions):
        return

    result = []
    for task in tasks:
        response = _task_actions[action](task, *args)
        req_info = dict(task_id=task, action=action, response=response)
        result.append(req_info)

    return result


def tasks_action(request, action):
    empty_response = HttpResponse('')

    if request.method != 'POST' or not (action in _task_actions):
        return empty_response

    data_json = request.body
    if not data_json:
        return empty_response
    data = json.loads(data_json)

    tasks = data.get("tasks")
    if not tasks:
        return empty_response

    params = data.get("parameters", [])
    response = do_tasks_action(tasks, action, *params)
    return HttpResponse(json.dumps(response))


def get_same_slice_tasks(request, tid):
    """ Getting
    :tid request: task ID
    :return: tasks of the same slice as specified (JSON)
    """
    empty_response = HttpResponse('')

    if not tid:
        return empty_response

    step_id = ProductionTask.objects.get(id=tid).step.id
    slice_id = StepExecution.objects.get(id=step_id).slice.id
    steps = [ str(x.get('id')) for x in StepExecution.objects.filter(slice=slice_id).values("id") ]
    tasks = [ str(x.get('id')) for x in ProductionTask.objects.filter(step__in=steps).values("id") ]

    response = dict(tasks=tasks)
    return HttpResponse(json.dumps(response))


@ensure_csrf_cookie
@csrf_protect
@never_cache
@datatables.datatable(ProductionTaskTable, name='fct')
def task_manage(request):
    qs = request.fct.get_queryset()
    last_task_submit_time = ProductionTask.objects.order_by('-submit_time')[0].submit_time



    return TemplateResponse(request, 'prodtask/_task_manage.html',
                            {'title': 'Manage Production Tasks',
                             'active_app': 'prodtask/task_manage',
                             'table': request.fct,
                             'parent_template': 'prodtask/_index.html',
                             'last_task_submit_time': last_task_submit_time,
                             'clouds': get_clouds(),
                             'sites': get_sites(),
                             'edit_mode': True,
                            })
