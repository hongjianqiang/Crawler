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


class KTable(object):
	"""docstring for KTable"""
	def __init__(self, node, K):
		self.node		= node
		self.K			= K
		self.buckets	= dict()

		# 初始化，生成空K-bucket桶
		for i in xrange(0,len(self.node[2])*4):
			self.buckets[i] = list()

		self.buckets[0].append(self.node)


	# 追加nid到K桶
	def append(self, node):
		distance = int(self.node[2], 16) ^ int(node[2], 16)
		num = len(bin(distance)) - 3	# 查找对应的K桶号（范围）
		
		flag = 'ignore'
		if 0 == len(self.buckets[num]):
			flag = 'insert'
		if len(self.buckets[num]) < self.K:
			for index, nodes in self.buckets.items():
				for n in nodes:
					# 过滤掉与K-Buckets里 IP 相同的node
					if n[0] == node[0]:
						flag = 'ignore'
						break
					else:
						flag = 'insert'
					# 过滤掉与K-Buckets里 ID 相同的node
					if n[2] == node[2]:	
						flag = 'ignore'
						break
					else:
						flag = 'insert'

		if 'insert' == flag:
			self.buckets[num].append(node)


	# 返回与目标node ID或infohash的最近K个node.
	def find_close_nodes(self, target):
		distance = int(self.node[2], 16) ^ int(target, 16)
		num = len(bin(distance)) - 3
		print "\nbuckets[%d]:" % num,
		return self.buckets[num]

	def show(self):
		print self.buckets

	def resp_ping(self):
		pass

	def resp_find_node(self):
		pass

	def resp_get_peers(self):
		pass

	def resp_announce_peer(self):
		pass

	def resp_krpc(self, krpc):
		if 'q' in krpc['y'].keys():
			if 'ping' in krpc['q'].keys():
				return self.resp_ping()
			elif 'find_node' in krpc['q'].keys():
				pass
			elif 'get_peers' in krpc['q'].keys():
				pass
			elif 'announce_peer' in krpc['q'].keys():
				pass
			else:
				return None
		else:
			return None



class KClient(object):
	"""docstring for KClient"""
	def __init__(self, nid, ktable):
		self.nid 		= nid
		self.ktable 	= ktable
		self.ufd 		= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.ufd.settimeout(5)

		for i in xrange(0,1000):
			random_id = os.urandom(20).encode('hex')
			self.ktable.append(('127.0.0.%d' % i, 6881, random_id))
	

	def close(self):
		self.ufd.close()


	def send_krpc(self, msg, address):
		self.ufd.sendto(bencode(msg), address)


	def ping(self, address):
		tid = os.urandom(4)		# token id
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
		msg = dict(
			t = tid,
			y = "q",
			q = "get_peers",
			a = dict(id = self.nid, info_hash = info_hash)
		)
		self.send_krpc(msg, address)
		return self.recv_krpc()


	# implied_port字段0表示和DHT共用一个端口下载种子文件，1表示使用后面的port字段端口下载种子文件。
	def announce_peer(self, address, info_hash=None, token=None, implied_port=1, port=1234):
		info_hash = info_hash if info_hash else self.nid
		token = token.decode('hex')
		tid = os.urandom(4) 	# token id
		msg = dict(
			t = tid,
			y = "q",
			q = "announce_peer",
			a = dict(id = self.nid, implied_port = implied_port, info_hash = info_hash, port = port, token = token)
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
	def __init__(self, nid, ktable):
		self.nid 		= nid
		self.ktable 	= ktable
		


class KAD(object):
	"""docstring for KAD"""
	def __init__(self, nid, port):
		self.K 		= 8
		self.nid  	= nid
		self.port 	= port
		self.ktable = KTable(('127.0.0.1',self.port,self.nid), self.K)
		self.kclient= KClient(self.nid, self.ktable)
		self.kserver= KServer(self.nid, self.ktable)

	def show_buckets(self):
		self.ktable.show()

	def serve_forever(self):
		pass
		


def random_id():
	hash = sha1()
	hash.update(os.urandom(20))
	return hash.digest()


if '__main__'==__name__:
	nid = random_id().encode('hex')
	tid = random_id().encode('hex')
	print 'node id : %s' % nid
	print 'Target id : %s' % tid
	print ''

	kad = KAD(nid, 6881)
	#kad.show_buckets()

	'''
	kcli = KClient(nid)

	print 'ping : '
	print kcli.ping(('127.0.0.1', 6881))
	print '\n'

	print 'find_node : '
	print kcli.find_node(('127.0.0.1', 6881), tid)
	print '\n'

	print 'get_peers : '
	print kcli.get_peers(('127.0.0.1', 6881), tid)
	print '\n'

	print 'resp_krpc : '
	print kcli.resp_krpc(tid)
	print '\n'
	'''

	raw_input()
		