import json
import logging

from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_protect
from .views import form_existed_step_list, form_step_in_page

from .models import StepExecution, InputRequestList, TRequest, Ttrfconfig, ProductionTask

_logger = logging.getLogger('prodtaskwebui')


@csrf_protect
def tag_info(request, tag_name):
    if request.method == 'GET':
        results = {'success':False}
        try:
            trtf = Ttrfconfig.objects.all().filter(tag=tag_name[0], cid=int(tag_name[1:]))
            if trtf:
                results.update({'success':True,'name':tag_name,'output':trtf[0].formats,'transformation':trtf[0].trf,
                                'input':trtf[0].input,'step':trtf[0].step})
        except Exception,e:
            pass
        return HttpResponse(json.dumps(results), content_type='application/json')

@csrf_protect
def clone_slices_in_req(request, reqid, step_from, make_link_value):
    if request.method == 'POST':
        results = {'success':False}
        try:
            data = request.body
            input_dict = json.loads(data)
            slices = input_dict
            ordered_slices = map(int,slices)
            ordered_slices.sort()
            #form levels from input text lines
            #create chains for each input
            new_slice_number = InputRequestList.objects.filter(request=reqid).count()
            current_request = TRequest.objects.get(reqid=reqid)
            old_new_step = {}
            if make_link_value == '1':
                make_link = True
            else:
                make_link = False
            step_from = int(step_from)
            for slice_number in ordered_slices:
                current_slice = InputRequestList.objects.filter(request=reqid,slice=int(slice_number))
                new_slice = current_slice.values()[0]
                new_slice['slice'] = new_slice_number
                new_slice_number += 1
                del new_slice['id']
                new_input_data = InputRequestList(**new_slice)
                new_input_data.save()
                step_execs = StepExecution.objects.filter(slice=current_slice)
                ordered_existed_steps, parent_step = form_existed_step_list(step_execs)
                if current_request.request_type == 'MC':
                    STEPS = StepExecution.STEPS
                else:
                    STEPS = ['']*len(StepExecution.STEPS)
                step_as_in_page = form_step_in_page(ordered_existed_steps,STEPS)
                first_changed = not make_link
                for index,step in enumerate(step_as_in_page):
                    if step:
                        if (index >= step_from) or (not make_link):
                            self_looped = step.id == step.step_parent.id
                            old_step_id = step.id
                            step.id = None
                            step.step_appr_time = None
                            step.step_def_time = None
                            step.step_exe_time = None
                            step.step_done_time = None
                            step.slice = new_input_data
                            if (step.status == 'Skipped') or (index < step_from):
                                step.status = 'NotCheckedSkipped'
                            elif step.status == 'Approved':
                                step.status = 'NotChecked'
                            if first_changed and (step.step_parent.id in old_new_step):
                                step.step_parent = old_new_step[int(step.step_parent.id)]
                            step.save_with_current_time()
                            if self_looped:
                                step.step_parent = step
                            first_changed = True
                            step.save()
                            old_new_step[old_step_id] = step
        except Exception,e:
            pass
        return HttpResponse(json.dumps(results), content_type='application/json')

@csrf_protect
def reject_slices_in_req(request, reqid):
    if request.method == 'POST':
        results = {'success':False}
        try:
            data = request.body
            input_dict = json.loads(data)
            slices = input_dict
            for slice_number in slices:
                current_slice = InputRequestList.objects.filter(request=reqid,slice=int(slice_number))
                new_slice = current_slice.values()[0]
                step_execs = StepExecution.objects.filter(slice=current_slice)
                ordered_existed_steps, parent_step = form_existed_step_list(step_execs)
                for step in ordered_existed_steps:
                    if ProductionTask.objects.filter(step=step).count() == 0:
                        step.step_appr_time = None
                        if step.status == 'Skipped':
                            step.status = 'NotCheckedSkipped'
                        elif step.status == 'Approved':
                            step.status = 'NotChecked'
                        step.save()
        except Exception,e:
            pass
        return HttpResponse(json.dumps(results), content_type='application/json')

@csrf_protect
def step_params_from_tag(request, reqid):
    if request.method == 'POST':
        results = {'success':False}
        try:
            data = request.body
            checkecd_tag_format = json.loads(data)
            tag = checkecd_tag_format['tag_format'].split(':')[0]
            output_format, slice_from = checkecd_tag_format['tag_format'].split('-')
            output_format = output_format[len(tag)+1:]
            project_mode = ''
            input_events = ''
            priority = ''
            nEventsPerJob = ''
            nEventsPerInputFile = ''
            destination_token = ''
            req = TRequest.objects.get(reqid=reqid)
            slices = InputRequestList.objects.filter(request=req).order_by("slice")
            for slice in slices:
                if slice.slice>=int(slice_from):
                    step_execs = StepExecution.objects.filter(slice=slice)
                    for step_exec in step_execs:
                        if(tag == step_exec.step_template.ctag)and(output_format == step_exec.step_template.output_formats):
                            task_config = json.loads(step_exec.task_config)
                            if 'project_mode' in task_config:
                                project_mode = task_config['project_mode']
                            if 'nEventsPerJob' in task_config:
                                nEventsPerJob = task_config['nEventsPerJob']
                            if 'nEventsPerInputFile' in task_config:
                                nEventsPerInputFile = task_config['nEventsPerInputFile']
                            if 'token' in task_config:
                                destination_token = task_config['token']
                            input_events = step_exec.input_events
                            priority = step_exec.priority
            results.update({'success':True,'project_mode':project_mode,'input_events':str(input_events),
                            'priority':str(priority),'nEventsPerJob':str(nEventsPerJob),
                            'nEventsPerInputFile':str(nEventsPerInputFile),'destination':destination_token})
        except Exception,e:
            pass
        return HttpResponse(json.dumps(results), content_type='application/json')


@csrf_protect
def update_project_mode(request, reqid):
    if request.method == 'POST':
        results = {'success':False}
        updated_slices = []
        try:
            data = request.body
            checkecd_tag_format = json.loads(data)
            tag = checkecd_tag_format['tag_format'].split(':')[0]
            output_format, slice_from = checkecd_tag_format['tag_format'].split('-')
            output_format = output_format[len(tag)+1:]
            slice_from = 0
            new_project_mode = checkecd_tag_format['project_mode']
            new_input_events = int(checkecd_tag_format['input_events'])
            new_priority = int(checkecd_tag_format['priority'])
            new_nEventsPerInputFile = None
            if checkecd_tag_format['nEventsPerInputFile']:
                new_nEventsPerInputFile = int(checkecd_tag_format['nEventsPerInputFile'])
            new_nEventsPerJob = None
            if checkecd_tag_format['nEventsPerJob']:
                new_nEventsPerJob = int(checkecd_tag_format['nEventsPerJob'])
            new_destination = None
            if checkecd_tag_format['destination_token']:
                new_destination = checkecd_tag_format['destination_token']
            req = TRequest.objects.get(reqid=reqid)
            slices = InputRequestList.objects.filter(request=req).order_by("slice")
            for slice in slices:
                if slice.slice>=int(slice_from):
                    step_execs = StepExecution.objects.filter(slice=slice)
                    for step_exec in step_execs:
                        if(tag == step_exec.step_template.ctag)and(output_format == step_exec.step_template.output_formats):
                            if step_exec.status != 'Approved':
                                task_config = json.loads(step_exec.task_config)
                                task_config['project_mode'] = new_project_mode
                                step_exec.task_config = ''
                                step_exec.set_task_config(task_config)
                                if new_nEventsPerInputFile:
                                    step_exec.set_task_config({'nEventsPerInputFile':new_nEventsPerInputFile})
                                if new_nEventsPerJob:
                                    step_exec.set_task_config({'nEventsPerJob':new_nEventsPerJob})
                                if new_destination:
                                    step_exec.set_task_config({'token':'dst:'+new_destination.replace('dst:','')})
                                step_exec.input_events = new_input_events
                                step_exec.priority = new_priority
                                step_exec.save()
                                if slice.slice not in updated_slices:
                                   updated_slices.append(str(slice.slice))
            results.update({'success':True,'slices':updated_slices})
        except Exception,e:
            pass
        return HttpResponse(json.dumps(results), content_type='application/json')

@csrf_protect
def get_tag_formats(request, reqid):
    if request.method == 'GET':
        results = {'success':False}
        try:
            tag_formats = []
            #slice_from = []
            #project_modes = []
            req = TRequest.objects.get(reqid=reqid)
            slices = InputRequestList.objects.filter(request=req).order_by("slice")
            for slice in slices:
                step_execs = StepExecution.objects.filter(slice=slice)
                for step_exec in step_execs:
                    tag_format = step_exec.step_template.ctag + ":" + step_exec.step_template.output_formats
                    task_config = '{}'
                    if step_exec.task_config:
                        task_config = step_exec.task_config
                    task_config = json.loads(task_config)
                    project_mode = ''
                    if 'project_mode' in task_config:
                        project_mode = task_config['project_mode']
                    do_update = True
                    for existed_tag_format in tag_formats:
                        if (existed_tag_format[0] == tag_format) and (existed_tag_format[1] == project_mode):
                            do_update = False
                    if do_update:
                        tag_formats.append((tag_format,project_mode,slice.slice))
            results.update({'success':True,'data':[x[0]+'-'+str(x[2]) for x in tag_formats]})
        except Exception,e:
            pass
        return HttpResponse(json.dumps(results), content_type='application/json')

@csrf_protect
def slice_steps(request, reqid, slice_number):
    if request.method == 'GET':
        results = {'success':False}
        try:
            req = TRequest.objects.get(reqid=reqid)
            input_list = InputRequestList.objects.get(request=req,slice=slice_number)
            existed_steps = StepExecution.objects.filter(request=req, slice=input_list)
            # Check steps which already exist in slice, and change them if needed
            ordered_existed_steps, existed_foreign_step = form_existed_step_list(existed_steps)
            result_list = []
            if req.request_type == 'MC':
                step_as_in_page = form_step_in_page(ordered_existed_steps,StepExecution.STEPS)
            else:
                step_as_in_page = form_step_in_page(ordered_existed_steps,['']*len(StepExecution.STEPS))
            if existed_foreign_step:
                    result_list.append({'step':existed_foreign_step.step_template.ctag,'step_name':'','step_type':'foreign',
                                        'nEventsPerJob':'','nEventsPerInputFile':'','nFilesPerJob':'',
                                        'project_mode':'','input_format':'',
                                        'priority':'', 'output_formats':'','input_events':'',
                                        'token':''})
            step_as_in_page = step_as_in_page[:-1]
            for step in step_as_in_page:
                if not step:
                    result_list.append({'step':'','step_name':'','step_type':''})
                else:
                    is_skipped = 'not_skipped'
                    if step.status == 'NotCheckedSkipped' or step.status == 'Skipped':
                        is_skipped = 'is_skipped'
                    task_config = json.loads(step.task_config)
                    result_list.append({'step':step.step_template.ctag,'step_name':step.step_template.step,'step_type':is_skipped,
                                        'nEventsPerJob':task_config.get('nEventsPerJob',''),'nEventsPerInputFile':task_config.get('nEventsPerInputFile',''),
                                        'project_mode':task_config.get('project_mode',''),'input_format':task_config.get('input_format',''),
                                        'priority':str(step.priority), 'output_formats':step.step_template.output_formats,'input_events':str(step.input_events),
                                        'token':task_config.get('token',''),'merging_tag':task_config.get('merging_tag',''),
                                        'nFilesPerMergeJob':task_config.get('nFilesPerMergeJob',''),'nGBPerMergeJob':task_config.get('nGBPerMergeJob',''),
                                        'nMaxFilesPerMergeJob':task_config.get('nMaxFilesPerMergeJob',''),
                                        'nFilesPerJob':task_config.get('nFilesPerJob','')})

            dataset = ''
            if input_list.dataset:
                dataset = input_list.dataset.name
            results = {'success':True,'step_types':result_list, 'dataset': dataset}
        except Exception,e:
            pass
        return HttpResponse(json.dumps(results), content_type='application/json')

@csrf_protect
def reject_steps(request, reqid, step_filter):
    if request.method == 'GET':
        results = {'success':False}
        try:
            changed_steps = 0
            if step_filter == 'all':
                req = TRequest.objects.get(reqid=reqid)
                steps = StepExecution.objects.filter(request=req)
                for step in steps:
                    if step.status == 'Approved':
                        step.status = 'NotChecked'
                        step.save()
                        changed_steps += 1
                    elif step.status == 'Skipped':
                        step.status = 'NotCheckedSkipped'
                        step.save()
                        changed_steps += 1
            results = {'success':True,'step_changed':str(changed_steps)}
        except Exception,e:
            pass
        return HttpResponse(json.dumps(results), content_type='application/json')