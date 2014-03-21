

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import Context, Template, RequestContext
from django.template.loader import get_template
from django.template.response import TemplateResponse
import core.datatables as datatables

from .forms import ProductionTaskForm, ProductionTaskCreateCloneForm, ProductionTaskUpdateForm
from .models import ProductionTask, TRequest

from django.db.models import Count

def task_details(request, rid=None):
   if rid:
       try:
           task = ProductionTask.objects.get(id=rid)
          # form = ProductionTaskForm(instance=req)
       except:
           return HttpResponseRedirect('/')
   else:
       return HttpResponseRedirect('/')

   return render(request, 'prodtask/_task_detail.html', {
       'active_app' : 'prodtask',
       'pre_form_text' : 'ProductionTask details with ID = %s' % rid,
       'task': task,
       'fields': task._meta.get_all_field_names(),
       'parent_template' : 'prodtask/_index.html',
   })

def task_clone(request, rid=None):
   if request.method == 'POST':
       form = ProductionTaskCreateCloneForm(request.POST)
       if form.is_valid():
          # Process the data in form.cleaned_data
           req = ProductionTask(**form.cleaned_data)
           req.save()
           return HttpResponseRedirect('/prodtask/task/%s' % req.id) # Redirect after POST
   else:
       try:
           values = ProductionTask.objects.values().get(id=rid)
       except:
           return HttpResponseRedirect('/')
       del values['id']
       form = ProductionTaskCreateCloneForm(values)

   return render(request, 'prodtask/_form.html', {
       'active_app' : 'prodtask',
       'pre_form_text' : 'Clonning of ProductionTask with ID = %s' % rid,
       'form': form,
       'submit_url': 'prodtask:task_clone',
       'url_args'  : rid,
       'parent_template' : 'prodtask/_index.html',
   })

def task_update(request, rid=None):
   if request.method == 'POST':
       try:
           req = ProductionTask.objects.get(id=rid)
           form = ProductionTaskUpdateForm(request.POST, instance=req) # A form bound to the POST data
       except:
           return HttpResponseRedirect('/')
       if form.is_valid():
          # Process the data in form.cleaned_data
           req = ProductionTask(**form.cleaned_data)
           req.save()
           return HttpResponseRedirect('/prodtask/task/%s' % req.id) # Redirect after POST
   else:
       try:
           req = ProductionTask.objects.get(id=rid)
           form = ProductionTaskUpdateForm(instance=req)
       except:
           return HttpResponseRedirect('/')
   return render(request, 'prodtask/_form.html', {
       'active_app' : 'prodtask',
       'pre_form_text' : 'Updating of ProductionTask with ID = %s' % rid,
       'form': form,
       'submit_url': 'prodtask:task_update',
       'url_args': rid,
       'parent_template' : 'prodtask/_index.html',
   })

def task_create(request):
   if request.method == 'POST': # If the form has been submitted...
       form = ProductionTaskCreateCloneForm(request.POST) # A form bound to the POST data
       if form.is_valid(): # All validation rules pass
           # Process the data in form.cleaned_data
           req = ProductionTask(**form.cleaned_data)
           req.save()
           return HttpResponseRedirect('/prodtask/trequest/%s' % req.id) # Redirect after POST
   else:
       form = ProductionTaskCreateCloneForm() # An unbound form
   return render(request, 'prodtask/_form.html', {
       'active_app' : 'prodtask',
       'pre_form_text' : 'Create ProductionTask',
       'form': form,
       'submit_url': 'prodtask:task_create',
       'parent_template' : 'prodtask/_index.html',
   })



class ProductionTaskTable(datatables.DataTable):

    id = datatables.Column(
        label='ID',
        )

    step = datatables.Column(
        label='StepEx',
        model_field='step__id',
        bVisible='false',        
        )

    request = datatables.Column(
        label='Request',
        model_field='request__reqid',
        bVisible='false',
        )

    parent_id = datatables.Column(
        label='Parent id',
        bVisible='false',
        )

    name = datatables.Column(
        label='Name',
        )

    project = datatables.Column(
        label='Project',
        bVisible='false',
#        sSearch='user',
        )

    status = datatables.Column(
        label='Status',
        )
        
    phys_group = datatables.Column(
        label='Phys group',
        )
        
    provenance = datatables.Column(
        label='Provenance',
        )

    total_events = datatables.Column(
        label='Total events',
        )

    total_req_jobs = datatables.Column(
        label='Total req jobs',
        )

    total_done_jobs = datatables.Column(
        label='Total done jobs',
        )

    submit_time = datatables.Column(
        label='Submit time',
        )
        
    start_time = datatables.Column(
        label='Start time',
        )
        
    timestamp = datatables.Column(
        label='Timestamp',
        )

    bug_report = datatables.Column(
        label='Bug report',
        )

    priority = datatables.Column(
        label='Priority',
        )
        
#    comments = datatables.Column(
#        label='Comments',
#        )
        
#    inputdataset = datatables.Column(
#        label='Inputdataset',
#        )
        
    physics_tag = datatables.Column(
        label='Physics tag',
        )

    class Meta:
        model = ProductionTask
        
        id = 'task_table'
        var = 'taskTable'
        bSort = True
        bPaginate = True
        bJQueryUI = True

        sScrollX = '100%'
        sScrollY = '25em'
        bScrollCollapse = True

        aaSorting = [[0, "desc"]]
        aLengthMenu = [[20, 100, -1], [20, 100, "All"]]
        iDisplayLength = 20
        fnRowCallback =  """
                        function( nRow, aData, iDisplayIndex, iDisplayIndexFull )
                        {
                            $('td:eq(0)', nRow).html('<a href="/prodtask/task/'+aData[0]+'/">'+aData[0]+'</a>&nbsp;&nbsp;'/*+
                                                     '<span style="float: right;" ><a href="/prodtask/task_update/'+aData[0]+'/">Update</a>&nbsp;'+
                                                     '<a href="/prodtask/task_clone/'+aData[0]+'/">Clone</a></span>'*/
                            );
                          /*  $('td:eq(1)', nRow).html('<a href="/prodtask/stepex/'+aData[1]+'/">'+aData[1]+'</a>');
                            $('td:eq(2)', nRow).html('<a href="/prodtask/request/'+aData[2]+'/">'+aData[2]+'</a>');*/
							$('td:eq(2)', nRow).html('<span class="'+aData[6]+'">'+aData[6]+'</span>');
							
							$('td:eq(8)', nRow).html( aData[12]=='None'? 'None' : aData[12].slice(0,-6) );
							$('td:eq(9)', nRow).html( aData[13]=='None'? 'None' : aData[13].slice(0,-6) );
							$('td:eq(10)', nRow).html( aData[14]=='None'? 'None' : aData[14].slice(0,-13)  );
                        }"""

        bServerSide = True
        sAjaxSource = '/prodtask/task_table/'
        



@datatables.datatable(ProductionTaskTable, name='fct')
def task_table(request):
    qs = request.fct.get_queryset()
    request.fct.update_queryset(qs)
    
    status_stat = ProductionTask.objects.values('status').annotate(count=Count('id'))
    total_task = ProductionTask.objects.count()
    projects = ProductionTask.objects.values('project').annotate(count=Count('id'))
    parents = ProductionTask.objects.values('parent_id').annotate(count=Count('id')).order_by('-parent_id')
    requests = ProductionTask.objects.values('request__reqid').annotate(count=Count('id'))
    return TemplateResponse(request, 'prodtask/_task_table.html', { 'title': 'Production Tasks Table',
                                                                    'active_app' : 'prodtask',
                                                                    'table': request.fct,
                                                                    'parent_template': 'prodtask/_index.html',
                                                                    'status_stat' : status_stat,
                                                                    'total_task' : total_task,
                                                                    'projects'  : projects,
                                                                    'requests'  : requests,
                                                                    'parents'   : parents,
                                                                    })

