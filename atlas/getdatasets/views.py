import json
import logging

from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import RequestForm

from .models import ProductionDatasetsExec

#Django-tables2
import django_tables2 as tables
import itertools

_logger = logging.getLogger('prodtaskwebui')

def request_data(req):
	if req.startswith('data'):
        	return request_data_dq2(req)
	else:
		return request_data_table(req)


def request_data_table(req):
	_logger.debug("Search for datasets in DB")
        req=req.replace('*','%')
        values = ProductionDatasetsExec.objects.extra(where=['name like %s'], params=[req]).exclude(status__iexact = u'deleted')
        dslist = values.values('name')
        counter = itertools.count()
        outlist=[]
        for ds in dslist:
                data_dict={}
                data_dict['name'] = ds['name']
                #data_dict['size'] = 
                data_dict['selection'] = ds['name']
                data_dict['number'] = u'%d' % next(counter)
                outlist.append(data_dict)

        return outlist

def request_data_dq2(req):
	_logger.debug("Search for datasets in DQ2")
	outputdq2={}
	try:
		#To work with DQ2
		from dq2.clientapi.DQ2 import DQ2
        	dq2 = DQ2()
        	outputdq2 = dq2.listDatasets(dsn=req,onlyNames=True)
	except ImportError, e:
		_logger.error("No DQ2")
		raise e
	except Exception, e:
		raise e
        dslist = list(outputdq2) 
        counter = itertools.count()
	outlist=[]
        for ds in dslist:
	        data_dict={}
		data_dict['name'] = ds
		data_dict['size'] = dq2.getDatasetSize(ds)
		if  data_dict['size'] != 0:
			data_dict['selection'] = ds
			data_dict['number'] = u'%d' % next(counter)
                	outlist.append(data_dict) 
        return outlist

class ProductionDatasetsTable(tables.Table):
        num = tables.Column(empty_values=(),orderable=False)
	name = tables.Column(orderable=False)
	selection = tables.CheckBoxColumn(attrs = { "th__input":
                                        {"onclick": "toggle(this)"}},
                                        orderable=False )

	def __init__(self, *args, **kwargs):
		super(ProductionDatasetsTable, self).__init__(*args, **kwargs)
		self.counter = itertools.count(1)

	def render_num(self):
		return '%d' % next(self.counter)

def request_data_form(request):
        if request.method == 'POST':
                form = RequestForm(request.POST)
                pks = request.POST.getlist("selection")
		if pks:
			#print list(pks)
			return HttpResponse(json.dumps(list(pks)), content_type="application/json")
		else:
                	if form.is_valid():
                        	req = form.cleaned_data['request']
                                dslist = request_data(req)
				table=ProductionDatasetsTable(dslist)
                        	return render(request, '_request_table.html', {
                        	'active_app': 'getdatasets',
                        	'pre_form_text': 'Request datasets',
                        	'form': form,
				'table': table,
                        	'submit_text': 'Select',
                        	'submit_url': 'getdatasets:request_data_form',
                        	'parent_template': 'prodtask/_index.html',
                        	})

        else:
                form = RequestForm()
                return render(request, '_request_table.html', {
                'active_app': 'getdatasets',
                'pre_form_text': 'Request datasets',
                'form': form,
                'submit_url': 'getdatasets:request_data_form',
                'parent_template': 'prodtask/_index.html',
                })

