#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from M2Crypto.BIO import MemoryBuffer
from M2Crypto.RSA import load_key_string, load_pub_key_bio, pkcs1_padding
import os.path
import sys

class rsautil:
	def __init__(self, keydata=None, pkeydata=None):
		self.key=load_key_string(keydata)
		membuf = MemoryBuffer(pkeydata)
		self.pkey=load_pub_key_bio(membuf)
		
	def encpublickey(self, plaindata):
		if self.pkey==None:
			return None
		maxenclen = len(self.pkey) - 11
		start = 0
		datalen = len(plaindata)
		cipherdata = ''
		while start < datalen:
			left = datalen - start
			if left > maxenclen:
				enclen = maxenclen
			else:
				enclen = left
			cipherdata += self.pkey.public_encrypt(plaindata[start:start+enclen], pkcs1_padding)
			start += enclen
		return cipherdata
			
	def decprivatekey(self, cipherdata):
		if self.key==None:
			return None
		maxdeclen = len(self.key)
		start = 0
		datalen = len(cipherdata)
		plaindata = ''
		while start < datalen:
			left = datalen - start
			if left > maxdeclen:
				declen = maxdeclen
			else:
				declen = left
			plaindata += self.key.private_decrypt(cipherdata[start:start+declen], pkcs1_padding)
			start += declen
		return plaindata

if __name__=='__main__':
	if len(sys.argv)!=3:
		print "usage: %s [private key file] [public key file]\r\n" % sys.argv[0]
		sys.exit(-1)
	keyfile = sys.argv[1]
	pkeyfile = sys.argv[2]
	if not os.path.exists(keyfile) or not os.path.exists(pkeyfile):
		print "key file not found\r\n"
		sys.exit(-1)
	fp = open(keyfile, "rb")
	keydata = fp.read()
	fp.close()
	fp = open(pkeyfile, "rb")
	pkeydata = fp.read()
	fp.close()
	print "key files load ok\r\n"
	testdata = 'hora RSA'
	rsa = rsautil(keydata, pkeydata)
	cipher = rsa.encpublickey(testdata)
	if cipher==None:
		print "encrypt error\r\n"
		sys.exit(-1)
	plain = rsa.decprivatekey(cipher)
	if plain==None:
		print "decrypt error\r\n"
		sys.exit(-1)
	if plain!=testdata:
		print "decrypt result error\r\n"
		sys.exit(-1)
	print "enc/dec test OK\r\n"
