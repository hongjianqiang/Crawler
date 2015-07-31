#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DHTlib.py
'''
Author:			hong jianqiang <569250030@qq.com>
Filename:		KADlib.py
Last modified:  2015-07-28 21:00

Description:
'''

import os, socket

from bencode import bencode, bdecode
from hashlib import sha1



class KClient(object):
	"""docstring for KClient"""
	def __init__(self, nid):
		self.nid = nid
		self.ufd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.ufd.settimeout(5)
	

	def close(self):
		self.ufd.close()


	def send_krpc(self, msg, address):
		self.ufd.sendto(bencode(msg), address)


	def ping(self, address):
		tid = os.urandom(4)		# token id
		#print tid.encode('hex')
		msg = dict(
			t = tid,
			y = "q",
			q = "ping",
			a = dict(id = self.nid)
		)
		self.send_krpc(msg, address)
		return self.recv_krpc()


	def find_node(self, address, target=None):
		target = target if target else self.nid
		tid = os.urandom(4)		# token id
		#print tid.encode('hex')
		msg = dict(
			t = tid,
			y = "q",
			q = "find_node",
			a = dict(id = self.nid, target = target)
		)
		self.send_krpc(msg, address)
		return self.recv_krpc()


	def get_peers(self, address, info_hash=None):
		info_hash = info_hash if info_hash else self.nid
		tid = os.urandom(4)		# token id
		#print tid.encode('hex')
		msg = dict(
			t = tid,
			y = "q",
			q = "get_peers",
			a = dict(id = self.nid, info_hash = info_hash)
		)
		self.send_krpc(msg, address)
		return self.recv_krpc()


	def recv_krpc(self):
		try:
			(data, address) = self.ufd.recvfrom(1024)
		except Exception, e:
			self.close()
			print "ErrorInfo:", e
			exit()

		msg = bdecode(data)
		return msg



class KServer(object):
	"""docstring for KServer"""
	def __init__(self):
		print 'This is KServer.'
		


class KTable(object):
	"""docstring for KTable"""
	def __init__(self):
		print 'This is KTable.'



class KAD(object):
	"""docstring for KAD"""
	def __init__(self):
		pass

	def random_id(self):
		hash = sha1()
		hash.update(os.urandom(20))
		return hash.digest()

	def serve_forever(self):
		pass
		


if '__main__'==__name__:
	kad = KAD()
	nid = kad.random_id()
	tid = kad.random_id()
	print 'node id : %s' % nid.encode('hex')
	print 'Target id : %s' % tid.encode('hex')
	print '\n\n'

	kcli = KClient(nid)
	print 'find_node : '
	print kcli.find_node(('127.0.0.1', 6881), tid)
	print '\n\n'

	print 'get_peers : '
	print kcli.get_peers(('127.0.0.1', 6881), tid)
	print '\n\n'

	raw_input()
		