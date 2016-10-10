# -*- coding: utf-8 -*-

import urllib
import urllib2
import json
import random
from time import sleep, gmtime, strftime

from cookielib import CookieJar
fix_headers = [('User-agent', '空空狐 2.3.0 rv:183 (iPhone; iOS 10.0.1; zh_CN)'), ('Version', '2.3.0'), ('Os', 'iOS'), ('Accept-Encoding', 'gzip')]
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = fix_headers

phone = '13800138000'
DEBUG = 1

if DEBUG:
	print "[{}] Logging in to {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), phonenum)

# POST login
formdata = { "version" : 'iPhone6-10.0.1', "versionNum": '2.3.0', "password" : '2eb897b5cacf49e65bc9b6a89bed89b8', "username" : phonenum }
req = urllib2.Request('http://api.kongkonghu.com/login', urllib.urlencode(formdata), headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'})
response = opener.open(req, timeout=30)

if DEBUG:
	print "[{}] Log in response {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), response.read()) 

pagemax = 3
page = 1

while page <= pagemax:
	sleep(random.randint(1,3))
	if DEBUG:
		print "[{}] Fetching item list page {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), page) 
	formdata = { "pageNum" : page }
	req = urllib2.Request('http://api.kongkonghu.com/auth/order/buy/orders', urllib.urlencode(formdata), headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'})
	response = opener.open(req, timeout=30)
	obj = json.load(response)

	for order in obj['data']:
		# auto recieve
		if order['status'] == 'SHIPPED' and order['remainingTime'] < 800000:
			sleep(random.randint(1,5))
			formdata = { "orderId" : order['id'] }
			req = urllib2.Request('http://api.kongkonghu.com/auth/order/receiveproduct', urllib.urlencode(formdata), headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'})
			response = opener.open(req, timeout=30)
			if DEBUG:
				print "[{}] Confirming the delivery: {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), response.read()) 

		# auto review
		if order['status'] == 'COMPLETED' and order['review']:
			sleep(random.randint(1,5))
			print "auto review"
			formdata = { "bizId" : order['id'], "content": '', "level": '5' }
			req = urllib2.Request('http://api.kongkonghu.com//auth/reviews/add', urllib.urlencode(formdata), headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'})
			response = opener.open(req, timeout=30)
			if DEBUG:
				print "[{}] Reviewing: {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), response.read()) 

	page = page + 1
