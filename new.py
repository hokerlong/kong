# -*- coding: utf-8 -*-

import os
import signal
import subprocess
import time
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

DEBUG = 1
port = 8123
host = 'your.proxy.com'

phonenum = '13810011001'

try:
    count = int(sys.argv[1])
except (ValueError, IndexError):
    count = 1

def print_debug_log(message):
    print "[{}] {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), message) 

def sleep_random(min, max):
    sec = random.randint(min,max)
    if DEBUG:
        print_debug_log("Sleeping {}s...".format(format(sec)))
    sleep(sec)

def get_tunnel_pids(host, port):
    pids = subprocess.check_output(['pgrep', '-f', 'ssh.*'+str(port)+'.*'+host]).rstrip("\n").split("\n")
    return pids

def create_tunnel(host, port):
    ssh_process = subprocess.Popen('ssh -qfNCD '+str(port)+' '+host, universal_newlines=True,
                                                shell=True,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                stdin=subprocess.PIPE)
    while True:
        p = ssh_process.poll()
        if p is not None: break
        time.sleep(1)
    if p == 0:
        pids = get_tunnel_pids(host, port)
        if len(pids) == 1:
            return ssh_processes[0]
        else:
            raise RuntimeError, 'multiple (or zero?) tunnel ssh processes found: ' + str(ssh_processes) 
    else:
        raise RuntimeError, 'Error creating tunnel: ' + str(p) + ' :: ' + str(ssh_process.stdout.readlines())

def login(cj, phonenum):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = fix_headers

    # POST login
    formdata = { "version" : 'iPhone6-10.0.1', "versionNum": '2.3.0', "password" : '2eb897b5cacf49e65bc9b6a89bed89b8', "username" : phonenum }
    data_encoded = urllib.urlencode(formdata)
    req = urllib2.Request('http://api.kongkonghu.com/login', data_encoded, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'})
    response = opener.open(req)
    print_debug_log(response.read())

def newitem(cj, title, price, picfile, count):
    upload_opener = register_openers()
    upload_opener.add_handler(urllib2.HTTPCookieProcessor(cj))
    upload_opener.addheaders = fix_headers
    params = {'categoryId': '148', 'originalPrice': '0', 'currentPrice': price, 'description': title, 'brand': 'amazon', 'size': '', 'productName': 'amazon - '+title, 'condition': '1', 'releaseStatus': '0', 'productImages': open(picfile, "rb"), }

    datagen, headers = multipart_encode(params)
    request = urllib2.Request("http://api.kongkonghu.com/auth/product/add", datagen, headers)

    while count > 0:
        sleep_random(2,7)
        response = upload_opener.open(request)
        print_debug_log(response.read())
        count = count - 1

fix_headers = [('User-agent', '空空狐 2.3.0 rv:183 (iPhone; iOS 10.0.1; zh_CN)'), ('Version', '2.3.0'), ('Os', 'iOS'), ('Accept-Encoding', 'gzip')]
cj = CookieJar()

try:
    pid = create_tunnel(host, port)
    socks.set_default_proxy(socks.SOCKS5, "localhost", port)
    socket.socket = socks.socksocket

    login(cj, phonenum)

    price = '320'
    title = 'amazon $50充值'
    picfile = "item.jpg"

    newitem(cj, title, price, picfile, count)

    os.kill(int(pid), signal.SIGTERM)
except RuntimeError as e:
    os.kill(int(pid), signal.SIGTERM)
    print ":-("
    print e.message

