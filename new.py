# -*- coding: utf-8 -*-

import sys
import urllib
import urllib2
import socket
import socks
import random
from time import sleep
from cookielib import CookieJar
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

phonenum = '13800138001'
try:
    count = int(sys.argv[1])
except (ValueError, IndexError):
    count = 1

price = '320'
title = 'amazon $50充值'
fix_headers = [('User-agent', '空空狐 2.3.0 rv:183 (iPhone; iOS 10.0.1; zh_CN)'), ('Version', '2.3.0'), ('Os', 'iOS'), ('Accept-Encoding', 'gzip')]
cj = CookieJar()

socks.set_default_proxy(socks.SOCKS5, "localhost", 8000)
socket.socket = socks.socksocket

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = fix_headers

# POST login
formdata = { "version" : 'iPhone6-10.0.1', "versionNum": '2.3.0', "password" : '2eb897b5cacf49e65bc9b6a89bed89b8', "username" : phonenum }
data_encoded = urllib.urlencode(formdata)
req = urllib2.Request('http://api.kongkonghu.com/login', data_encoded, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'})
response = opener.open(req)
print response.read()

# new item
upload_opener = register_openers()
upload_opener.add_handler(urllib2.HTTPCookieProcessor(cj))
upload_opener.addheaders = fix_headers
params = {'categoryId': '148', 'originalPrice': '0', 'currentPrice': price, 'description': title, 'brand': 'amazon', 'size': '', 'productName': 'amazon - '+title, 'condition': '1', 'releaseStatus': '0', 'productImages': open("item.jpg", "rb"), }

datagen, headers = multipart_encode(params)
request = urllib2.Request("http://api.kongkonghu.com/auth/product/add", datagen, headers)

while count > 0:
    sec = random.randint(2,7)
    print "sleeping {}s...".format(sec)
    sleep(sec)
    response = upload_opener.open(request)
    print response.read()
    count = count - 1
