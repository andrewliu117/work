#!/usr/bin/env python
import sys

import fifo_dispatcher_conf

import Queue

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

### fifo
from fifo import FifoInterface
from fifo.ttypes import *
from fifo.FifoInterface import Iface


class dispatchHandler(Iface):
	def __init__(self, threadNum, adds_str):
		self.clients = Queue.Queue()
		self.threadNum = threadNum
		adds=[]
		for add in adds_str.split(","):
			adds.append(add.split(":"))
		idx = 0;
		for i in range(self.threadNum): 
			print adds[idx][0], adds[idx][1]
			transport = TSocket.TSocket(adds[idx][0], int(adds[idx][1]))
			transport = TTransport.TBufferedTransport(transport)
			protocol = TBinaryProtocol.TBinaryProtocol(transport)
			client = FifoInterface.Client(protocol)
			#transport.open()
			self.clients.put((client,transport))
			idx = (idx + 1) % len(adds)
	
	def __del__(self):
		for i in range(self.threadNUm):
			ct = self.client.get()
			ct[1].close()
			del ct

	def put(self, mate, value):
		ct = self.clients.get()
		try:
			if not ct[1].isOpen():
				#print "is  not open"
				ct[1].close()
			ct[1].open()
			#else:
				#print "is open"
			ret = ct[0].put(mate, value)
			ct[1].close()
			self.clients.put(ct)
			return ret
			#return ReturnCode.OK
		except:
			#ct[1].close()
			#ct[1].open()
			self.clients.put(ct)
			return ReturnCode.INTERNALERROR

if __name__ == "__main__" :
	handler = dispatchHandler(fifo_dispatcher_conf.OUT_THREADNUM, fifo_dispatcher_conf.OUT_ADDS)
	processor = FifoInterface.Processor(handler)
	transport = TSocket.TServerSocket(fifo_dispatcher_conf.GETTER_IP, fifo_dispatcher_conf.GETTER_PORT)
	tfactory = TTransport.TBufferedTransportFactory()
	pfactory = TBinaryProtocol.TBinaryProtocolFactory()
	
	#server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
	
	# You could do one of these for a multithreaded server
	#server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
	server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)
	server.setNumThreads(fifo_dispatcher_conf.GETTER_THREADNUM)

	print 'Starting the server...'
	server.serve()
	print 'done.'

