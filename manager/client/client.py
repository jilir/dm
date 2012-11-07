import socket
import os
import sys
import threading
import time
import urllib2
import random
import tarfile
import platform
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import subprocess


back_host = 'http://10.0.16.1:8000/'
pythonpath = 'C:\\Python27\\python2.7.exe'
peachpath = 'C:\\peach-svn\\peach.py'
peachdir = 'C:\\peach-svn\\'
curpath = os.path.dirname(__file__)
mymid = -1
mypid = -1
totalmachines = 0
skipto = -1
syspf = platform.system()


def upload_log(url, filename):
	global mymid
	global mypid
	print 'upload'
	register_openers()
	datagen, headers = multipart_encode({'file': open(filename, 'rb'), 'pid':str(mypid), 'mid':str(mymid)})
	request = urllib2.Request(url, datagen, headers)
	return urllib2.urlopen(request).read()



def tar_logs():
	global mymid
	global mypid
	global syspf
	pfpath = ''
	if(syspf == 'Windows'):
		pfpath = '\\'
	if(syspf == 'Linux'):
		pfpath = '/'
	print '33'
	if(skipto == -1):
		name = str(mypid)+'_'+str(mymid)
	else:
		name = str(mypid)+'_'+str(mymid)+'_'+str(skipto)
	
	tarname = 'log_'+name+'.tar'
	tar=tarfile.open(tarname,'w')
	
	for root,dir,files in os.walk(name+pfpath):
		for file in files:
			fullpath=os.path.join(root,file)
			tar.add(fullpath)
	tar.close()
	return tarname
def get_count():
	global peachdir
	while(os.path.isfile('status.txt') != True):
		time.sleep(1)
	
	while(1):
		fp = open( 'status.txt', 'r')
		txt = fp.read()
		fp.close()
		sp = txt.split('|')
		try:
			a = int(sp[0])
			b = int(sp[1])
			break;
		except:
			time.sleep(1)
		
	return a, b

def http_back(url):
	request = urllib2.urlopen(url)
	a=request.read()
	print a
	return a

def get_xml(pid):
	oldStdout = sys.stdout
	sys.stdout = open('network.log', 'w')
	back_uri = 'getxml/?pid='+str(pid)
	xml = http_back(back_host+back_uri)
	sys.stdout = oldStdout
	fp = open(str(pid)+'.tar', 'wb')
	fp.write(xml)
	fp.close()
	return str(pid)+'.tar'


def beat_th():
	global peachpath
	global pythonpath
	global mypid
	global mymid
	global totalmachines
	global skipto
	while(1):
		back_uri = ''
		if(mymid == -1 or mypid == -1):
			back_uri = 'gettask/'
			cmd = http_back(back_host+back_uri)
			todo = cmd.split('|')
			if(todo[0] == 'free'):
				print 'free'
			if(todo[0] == 'task'):
				mypid = int(todo[1])
				mymid = int(todo[2])
				totalmachines = int(todo[3])
				skipto = int(todo[4])
				xml_name = get_xml(mypid)
				if(skipto == -1):
					dirname = str(mypid)+'_'+str(mymid)
					ss = pythonpath+' '+peachpath+' -p '+str(totalmachines)+','+str(mymid)+' '+'xml.xml'
				else:
					dirname = str(mypid)+'_'+str(mymid)+'_'+str(skipto)
					ss = pythonpath+' '+peachpath+' -p '+str(totalmachines)+','+str(mymid)+' --skipto '+str(skipto)+' '+'xml.xml'
				os.mkdir(dirname)
				print dirname
				t = tarfile.open(xml_name, 'r')
				t.extractall(dirname)
				t.close()
				fp = open('status.txt', 'w')
				fp.write('0|0')
				fp.close()
				#path!!!
				os.chdir(dirname)
				#ss = pythonpath+' '+peachpath+' -p '+str(totalmachines)+','+str(mymid)+' '+'xml.xml'
				#threading.Thread(target=os.system, args=(ss,)).start()
				p = subprocess.Popen(ss,stdout= open('peach_run.log', 'w'))
				
				#p = subprocess.Popen(ss)
				#os.system('peach.py -p '+str(totalmachines)+','+str(mymid)+' '+dirname+'\\xml.xml')
				#op_th = threading.Thread(target = operation, args = (ss))
				#op_th.start()
				#child_pid = os.fork()
				#if(child_pid == 0):
					
		else:
			countnow,totalcount = get_count()
			if(totalcount - countnow < 5 and countnow != 0):
				print 'over'
				os.chdir(curpath)
				filename = tar_logs()
				back = upload_log(back_host+'upload_logs/',filename)
				if(back == 'copythat'):
					print 'upload ok'
					back = http_back(back_host+'iamfree/?mid='+str(mymid)+'&pid='+str(mypid))
					if(back == 'copythat'):
						mypid = -1
						mymid = -1
						totalmachines = 0
					else:
						print 'fk...'
				else:
					print 'upload error'
					continue
				
			else:
				back_uri = 'status/?cid='+str(countnow)+'&mid='+str(mymid)+'&pid='+str(mypid)+'&tid='+str(totalcount)
				ss = http_back(back_host+back_uri)
				if(ss == 'stop'):
					print 'error'

					#kill peach and goto gettask fuck the path!!!
					##need to add
		time.sleep(5)

'''
my_address = ('', 17878)
server_address = ('192.168.152.129', 18787)
to_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
to_listen.bind(my_address)
to_listen.listen(2)
'''
'''
tn = 0
while(1):
	try:
		rtn = http_back(back_host+'hi/')
		if(rtn == 'hi'):
			print 'server ok!'
			break
		else:
			print 'what?!'
	except:
		print 'Not Ready'
		time.sleep(1)

'''

bt_th = threading.Thread(target = beat_th, args = ())
bt_th.start()


while(1):
	time.sleep(10)
	continue
	'''
	ss, addr = to_listen.accept()
	str_cmd = ss.recv(102400)
	todo = str_cmd.split('|')
	if(todo[0] == 'xmlfile'):
		print 'save file'
		spli = todo[1]+'|'
		split2 = str_cmd.split(spli)
		fp = open(todo[1], 'w')
		fp.write(split2[1])
		fp.close()
		#send_back_server('back|fileok')
		#need send status back

	if(todo[0] == 'task'):
		print 'ff'
		mypid = int(todo[1])
		mymid = int(todo[2])
		totalmachines = int(todo[3])
		xml = todo[4]
		
	if(mymid == -1 or mypid == -1):
		#send back
		continue
'''
