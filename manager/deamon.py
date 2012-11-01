import socket
import threading
import thread
#from projects.models import xml

lock = thread.allocate_lock()

client_index = 0
client_table = {}
client_result = {}
cmd_index = 0

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

def send_all_client(ss):
	global client_table
	for keys in client_table.keys():
		if(cmp(client_table[keys], 'NULL') != 0):
			send_client(client_table[keys], ss)

def my_process(ss, addr):
	global client_index
	global client_table
	rsp_str = ss.recv(1024)
	cmd_str = rsp_str.split('|')
	#print cmd_str[0]
	if(cmp(cmd_str[0], 'getmyid') == 0):
		lock.acquire()
		str_num = str(client_index)
		#client_table[client_index:0] = addr[0]	
		client_table[client_index] = addr[0]
		client_index+=1
		print 'added a machine '+str_num+':'+addr[0]
		lock.release()
		to_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_addr = (addr[0], 17878)
		to_client.connect(client_addr)
		to_client.send('youridis|'+str_num)
		to_client.close()

	if(cmp(cmd_str[0], 'back') == 0):
		print cmd_str[1]
	
	if(cmp(cmd_str[0], 'iam') == 0):
		if(cmp(client_table[int(cmd_str[1])], addr[0]) != 0):
			#update
			#print 'update'
			client_table[int(cmd_str[1])] = addr[0]	
	

	ss.close()


def control():
	global client_index
	global client_table
	while(1):
		raw_cmd = raw_input('>')
		cmd = raw_cmd[0:raw_cmd.index(' ')]
		split_cmd = raw_cmd.split(' ')
		if(cmp(cmd, 'show_machines') == 0):
			for keys in client_table.keys():
				if(cmp(client_table[keys], 'NULL') != 0):
					print 'machine '+str(keys)+':'+client_table[keys]
		if(cmp(cmd,'exit') == 0):
			exit()
		if(cmp(cmd, 'exec') == 0):
			client_limit = raw_cmd[raw_cmd.index('TO ')+3:]
			print client_limit
			if(cmp(client_limit, 'ALL') == 0):
				for keys in client_table.keys():
					
					if(cmp(client_table[keys], 'NULL') != 0):
						send_client(client_table[keys], 'exec|'+raw_cmd[raw_cmd.index('exec ')+4:raw_cmd.index(' TO')])


			else:
				to_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				client_addr = (client_table[int(raw_cmd[raw_cmd.index('TO ')+3:])], 17878)
				to_client.connect(client_addr)
				to_client.send('exec|'+raw_cmd[raw_cmd.index('cmd ')+4:raw_cmd.index(' TO')])
				to_client.close()
		
		if(cmp(split_cmd[0], 'sendxml') == 0):
			#there should not place spaces in file path and name 
			fp = open(split_cmd[1], 'r')
			xml_cnt = fp.read()
			fp.close()
			#to_send = 'xmlfile|'+split_cmd[2]+'|'+xml_cnt
			#data_len = len(to_send)+len(str(len(to_send)))
			#to_send = 'xmlfile|'+str(data_len)+'|'+split_cmd[2]+'|'+xml_cnt
			#send_all_client(to_send)
			send_all_client('xmlfile|'+split_cmd[2]+'|'+xml_cnt)


def deamon_init():
	global client_table
	my_addr = ('', 18787)
	print 'hi~~'
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.bind(my_addr)
		s.listen(100)
	except:
		thread.exit()
	for idx in range(0,254):
		client_table[idx] = 'NULL'


	cth = threading.Thread(target = control, args = ())
	cth.start()
	fi = xml(path = 'test', description = '123', status='test')
	fi.save();
	while(1):
		ss, addr = s.accept()
		th = threading.Thread(target = my_process, args = (ss, addr))
		th.start()

	s.close()