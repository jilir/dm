from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django import forms
from projects.models import xml
from projects.models import projects
from projects.models import machines
from projects.models import logs
import datetime
import os
import time
import threading

free_block_switch = 0
mutex = threading.Lock()

def upload_xml(request):
	if request.method == 'POST':
		now = str(datetime.datetime.now())
		name = request.POST['name']
		description = request.POST['description']
		path = handle_uploaded_file(request.FILES['file'],'/xmls/'+now+'.tar')
		fi = xml(path = path, description = description, status='free')
		fi.save();
		return HttpResponseRedirect('/success/url/')
	else:
		return render_to_response('upload_xml.html')

def upload_logs(request):
	if request.method == 'POST':
		pid = int(request.POST['pid'])
		mid = int(request.POST['mid'])
		timest = int(time.time())
		name = 'log_'+ str(pid)+'_'+str(mid)
		print 'uploading ' + str(pid)+'_'+str(mid)
		#need some filter
		path = handle_uploaded_file(request.FILES['file'],'/logs/'+name+'.tar')
		machine = machines.objects.get(projectid=pid, macid=mid)
		log = logs(ip=machine.ip,projectid=pid,macid=mid,path=path, time=timest)
		log.save()
		return HttpResponse('copythat')
	else:
		#return HttpResponse('error')
		return render_to_response('upload_test.html')

def handle_uploaded_file(f, name):
	abpath = os.path.dirname(__file__)
	path = abpath+name
	with open(path, 'w') as destination:
		for chunk in f.chunks():
			destination.write(chunk)
	return path

def success(request):
	return HttpResponse('success')



def create_project(request):
	try:
		freenum = len(machines.objects.filter(status = 'free'))
	except:
		freenum = 0
	if request.method == 'POST':
		#print 'g'
		name = request.POST['name']
		description = request.POST['description']
		num = int(request.POST['number'])
		xmlid = int(request.POST['xmls'])
		if(freenum < num):
			return HttpResponse('too large')
		project = projects(name=name, description=description, totalmachines=num,xmlid=xmlid,allocindex=0,status='waiting')
		project.save()
		return HttpResponse('success')
	else:
		allproject = projects.objects.all()
		
		xmls = xml.objects.filter(status = 'free')
		return render_to_response('create_project.html', {'xmls':xmls, 'max':freenum, 'projects':allproject})

def send_client(addr, ss):
	try:
		to_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			client_addr = (addr, 17878)
			to_client.connect(client_addr)
			to_client.send(ss)
		finally:
			to_client.close()
	except:
		print 'connect ' + addr + ' error'

def send_all_client(clients,ss):
	for client in clients:
		send_client(client.ip, ss)
	
def start_one_machine(machine):
	print 'hello'

def start_p(request):
	if request.method == 'GET':
		pid = int(request.GET['pid'])
		start_project(pid)
	return HttpResponse('success')
def start_project(pid):
	#ffffkkkk   sync???
	mutex.acquire()
	#brute
	try:
		filetime = time.time()
		project = projects.objects.get(id=pid)
		name = project.name
		totalmachines = project.totalmachines
		xmlid = project.xmlid
		xmla = xml.objects.get(id=xmlid)
		try:
			freemachines = machines.objects.filter(status='free').order_by('ip')[0:totalmachines]
		except:
			print 'fk'
		if(len(freemachines) < totalmachines):
			print 'fk'
		#fp = open(xmla.path, 'r')
		#xmlcontent = fp.read()
		#fp.close()
		#cmd = 'xmlfile|'+name+'_'+str(filetime)+'.xml|'+xmlcontent
		#send_all_client(freemachines, cmd)
		#should wait until all recived
		#send_all_client(freemachines, 'task|')
		free_block_switch = 1
		for i in range(0, totalmachines):
			time2 = time.time()
			freemachines[i].projectid = pid
			freemachines[i].macid = i
			freemachines[i].status = 'inuse'
			freemachines[i].lastback = int(time2)
			freemachines[i].lastmodify = int(time2)
			freemachines[i].save()
			cmd = 'task|'+str(pid)+'|'+str(i)+'|'+str(totalmachines)+'|'+name+'_'+str(filetime)+'.xml'
		free_block_switch = 0
		project.allocindex = i
		project.status = 'running'
		project.save()
	finally:	
		mutex.release()


def statusback(request):
	if request.method == 'GET':
		pid = int(request.GET['pid'])
		mid = int(request.GET['mid'])
		cid = int(request.GET['cid'])
		tid = int(request.GET['tid'])
		timest = int(time.time())
		machine = machines.objects.get(projectid=pid, macid=mid)
		count = machine.countnow
		if(count != cid):
			machine.lastmodify = timest
		machine.countnow = cid
		machine.totalcount = tid
		machine.lastback = timest
		machine.save()
	return HttpResponse('copythat')

def get_xml(request):
	if request.method == 'GET':
		try:
			pid = int(request.GET['pid'])
		except:
			return HttpResponse('error')
		project = projects.objects.get(id=pid)

		#def returnfile(name, buf_size=262144):
		#	fp = open(name, 'rb')
		#	while(1):
		#		c = f.read(buf_size)
		#		if(c):
		#			yield c
		#		else:
		#			break
		#	fp.close()
		#application/x-tar
		#response = HttpResponse(mimetype='application/x-tar')
		#response = HttpResponse(mimetype='application/x-tar')
		#response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
		xmla = xml.objects.get(id=project.xmlid)
		fp = open(xmla.path, 'rb')
		c = fp.read()
		fp.close()
		return HttpResponse(c)
	return HttpResponse('error')

def get_task(request):
	if request.method == 'GET':
		timest = int(time.time())
		#need change
		ip = request.META['REMOTE_ADDR']
		try:
			machine = machines.objects.get(ip=ip)
		except machines.DoesNotExist:
			machine = machines(ip=ip, macid=-1, totalcount=-1, countnow=-1, projectid=-1, status='free', lastback=timest, lastmodify=timest)
			machine.save()
		
		if(machine.macid == -1 or machine.projectid == -1):
			machine.lastback=timest
			machine.lastmodify=timest
			machine.save()
			return HttpResponse('free')
		else:
			project = projects.objects.get(id=machine.projectid)
			cmd = 'task|'+str(project.id)+'|'+str(machine.macid)+'|'+str(project.totalmachines)
			return HttpResponse(cmd)
'''
def find_free_machine(request):
	if(free_block_switch == 1):
		return HttpResponse('wait-.-')
	timest = int(time.time())
	if request.method == 'GET':
		try:
			#ip = request.GET['ip']
			ip = request.META['REMOTE_ADDR']
			#need some auth
			machine = machines(ip=ip, macid=-1, totalcount=-1, countnow=-1, projectid=-1, status='free', lastback=timest, lastmodify=timest)
			machine.save()
		except:
			print 'fk'
	return HttpResponse('copythat')

def finish_task(request):
	print 'f'
'''
def find_free_machine(request):
	timest = int(time.time())
	if request.method == 'GET':
		pid = int(request.GET['pid'])
		mid = int(request.GET['mid'])
		machine = machines.objects.get(projectid=pid,macid=mid)
		try:
			log = logs.objects.get(projectid=pid,macid=mid)
		except:
			return HttpResponse('error')
		machine.projectid = -1
		machine.macid = -1
		machine.totalcount=-1
		machine.countnow=-1
		machine.status='free'
		machine.lastback=timest
		machine.lastmodify=timest
		machine.save()
		return HttpResponse('copythat')
	else:
		return HttpResponse('error')


def show_status(request):
	if request.method == 'GET':
		machine = machines.objects.all()
		xmls = xml.objects.all()
		project = projects.objects.all()
		log = logs.objects.all()
		crash = crashs.objects.all()
		return render_to_response('show_status.html', {'machines':machine,'xmls':xmls, 'projects':project, 'logs':log,'crashs':crash})
	else:
		return HttpResponse('error')

def show_hi(request):
	return HttpResponse('hi')
