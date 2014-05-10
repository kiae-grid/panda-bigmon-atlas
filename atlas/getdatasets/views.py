import json

from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import RequestForm

from .models import ProductionDatasetsExec
#To work with DQ2
from dq2.clientapi.DQ2 import DQ2
#Django-tables2
import django_tables2 as tables
import itertools

def request_data_table(request,req):
	print 'Request DB'
        req=req.replace('*','%')
        values = ProductionDatasetsExec.objects.extra(where=['name like %s'], params=[req]).exclude(status__iexact = u'deleted')
	#print values.query
        #values_list = values.values_list('name')
        #values_dict = values.values('name')
        dslist = values.values('name')
        counter = itertools.count()
        outlist=[]
        for ds in dslist:
                dict={}
                dict['name'] = ds['name']
                #dict['size'] = 
                #dict['selection'] = 'none'
                dict['selection'] = ds['name']
                dict['number'] = u'%d' % next(counter)
                outlist.append(dict)

        return outlist

def request_data_dq2(request,req):
	print 'Request dq2'
        dq2 = DQ2()
        output = dq2.listDatasets(dsn=req,onlyNames=True)
        #return HttpResponse(json.dumps(list(output)), content_type="application/json")
        dslist = list(output) 
        counter = itertools.count()
	outlist=[]
        for ds in dslist:
	        dict={}
		dict['name'] = ds
		dict['size'] = dq2.getDatasetSize(ds)
		if  dict['size'] != 0:
			#dict['selection'] = 'none'
			dict['selection'] = ds
			dict['number'] = u'%d' % next(counter)
                	outlist.append(dict) 
        return outlist

class ProductionDatasetsTable(tables.Table):
        num = tables.Column(empty_values=(),orderable=False)
	name = tables.Column(orderable=False)
	selection = tables.CheckBoxColumn(attrs = { "th__input":
#	selection = tables.CheckBoxColumn(accessor="pk", attrs = { "th__input": 
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
                        	if req.startswith('data'):
                                	dslist = request_data_dq2(request,req)
                        	else:
                                	dslist = request_data_table(request,req)
				table=ProductionDatasetsTable(dslist)
                        	return render(request, '_request_table2.html', {
                        	'active_app': 'getdatasets',
                        	'pre_form_text': 'Request datasets',
                        	'form': form,
				'table': table,
                        	'submit_text': 'Select',
                        	'submit_url': 'getdatasets:request_data_form',
                        	'parent_template': '_index.html',
                        	})

        else:
                form = RequestForm()
                return render(request, '_request_table2.html', {
                'active_app': 'getdatasets',
                'pre_form_text': 'Request datasets',
                'form': form,
                'submit_url': 'getdatasets:request_data_form',
                'parent_template': '_index.html',
                })


