"""
Temporary placeholder to exec Jedi client remotely.
To be replaced with upcoming DEFT API functions
"""

import ast
import json
import os.path
import re
import subprocess
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

import atlas.settings
from .models import InputRequestList, MCPriority, ProductionTask, StepExecution, StepTemplate

RSA_KEY_FILE = "%s/%s" % (os.path.dirname(os.path.abspath(atlas.settings.__file__)),
                          "jediclient-ssh/id_rsa")


def _exec_jedi_command(task_id, command, *params):
    """
    Perform JEDI command for the task.
    :param task_id: task ID
    :param command: command to perform
    :param params: additional command parameters for JEDI client
    :return: dict containing keys 'accepted', 'registered', 'jedi_message', 'jedi_status_code'
    """
    # TODO: add logging and permissions checking
    jedi_commands = ['killTask', 'finishTask', 'changeTaskPriority',
                     'reassignTaskToSite', 'reassignTaskToCloud']

    if not command in jedi_commands:
        raise ValueError("JEDI command not supported: '%s'" % (command))

    (task_id, params) = (str(task_id), [str(x) for x in params])
    action_call = "import jedi.client as jc; print jc.%s(%s)" % (command, ",".join(list([task_id])+params))

    proc = subprocess.Popen(['ssh', '-q',
                             '-i', RSA_KEY_FILE,
                             '-o', 'StrictHostKeyChecking=no',
                             '-o', 'UserKnownHostsFile=/dev/null',
                             '-o', 'LogLevel=QUIET',
                             'sbelov@aipanda015',
                             'PYTHONPATH=/mnt/atlswing/site-packages/ python -c "%s"' % (action_call),
                             '2>/dev/null'
                            ],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = proc.communicate()
    bash_lines = re.compile("^bash:")
    # removing shell warnings if any
    out = [x.rstrip() for x in out if not bash_lines.match(x)]
    out = filter(None, out)  # remove empty lines

    result = {}
    if not out:
        return result

    jedi_response = tuple(ast.literal_eval(out[0]))
    if not jedi_response:
        return result

    (accepted, registered, message) = (False, False, '')
    (status_code, return_code) = (0, 0)

    status_code = jedi_response[0]
    if status_code == 0:
        accepted = True

        if command == "changeTaskPriority":
            return_code = jedi_response[1]
        else:
            (return_code, message) = jedi_response[1]
        registered = bool(return_code)
        result['jedi_return_code'] = return_code
    else:
        message = jedi_response[1]

    result.update(accepted=accepted, registered=registered,
                  jedi_message=message, jedi_status_code=status_code)

    return result


def kill_task(task_id):
    """
    Kill task with all it jobs.
    :param task_id: ID of task to kill
    :return: dict with action status
    """
    return _exec_jedi_command(task_id, "killTask")


def finish_task(task_id):
    """
    Finish task with all it jobs.
    :param task_id: task ID
    :return: dict with action status
    """
    return _exec_jedi_command(task_id, "finishTask")


def obsolete_task(task_id):
    """
    Mark task as 'obsolete'
    :param task_id: task ID
    :return: dict with action status
    """
    # TODO: add logging and permissions checking
    try:
        task = ProductionTask.objects.get(id=task_id)
    except ObjectDoesNotExist:
        return dict(accepted=True, registered=False, message="Task %s does not exist")
    except Exception as error:
        return dict(accepted=True, registered=False, message=error)

    if task.status not in ['done', 'finished']:
        return {}

    #TODO: log action
    ProductionTask.objects.filter(id=task_id).update(status='obsolete', timestamp=timezone.now())
    return dict(accepted=True, registered=True)


def change_task_priority(task_id, priority):
    """
    Set task JEDI priority.
    :param task_id:
    :param priority: JEDI task priority
    :return: dict with action status
    """
    return _exec_jedi_command(task_id, "changeTaskPriority", priority)


def get_step_priority(priority_key, step_name):
    """ Get JEDI priority from the step template
    :param priority_key: priority level (<100)
    :param step_name: name of the step in question
    :return: value of JEDI priority of the step
    """
    try:
        mc_priority = MCPriority.objects.get(priority_key=priority_key)
    except ObjectDoesNotExist:
        return
    priority_dict = json.loads(mc_priority.priority_dict)
    if step_name in priority_dict:
        return priority_dict[step_name]
    else:
        return


def get_task_priority_level(task_id):
    """
    Get task priority level (if any) and
    :param task_id:
    :return:
    """

    result = dict(id=task_id, successful=False, level=None, priority=None)

    try:
        task = ProductionTask.objects.get(id=task_id)
    except ObjectDoesNotExist:
        result.update(reason="Task not found")
        return result

    step = task.step
    input_dataset = step.slice
    priority = input_dataset.priority

    if priority < 100: # having a priority level here
        step_name = step.step_template.step
        priority_value = get_step_priority(priority, step_name)
        result.update(level=priority, priority=priority_value)
    else: # just a plain priority
        result.update(priority=priority, reason="")

    result.update(successful=True)
    return result


def change_task_priority_level(task_id):
    """

    :param task_id:
    :return:
    """
    try:
        task = ProductionTask.objects.get(id=task_id)
    except:
        pass


def increase_task_priority(task_id):
    pass

def decrease_task_priority(task_id):
    pass


def reassign_task_to_site(task_id, site):
    """
    Reassign task to specified site.
    :param task_id: task ID
    :param site: site name
    :return: dict with action status
    """
    return _exec_jedi_command(task_id, "reassignTaskToSite", site)


def reassign_task_to_cloud(task_id, cloud):
    """
    Reassign task to specified cloud
    :param task_id: task ID
    :param cloud: cloud name
    :return: dict with action status
    """
    return _exec_jedi_command(task_id, "reassignTaskToCloud", cloud)

