#!/usr/bin/env python
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
import json
from time import sleep, gmtime, strftime
from cookielib import CookieJar
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

DEBUG = 1
INFO = 2
ERROR = 3

log_level = INFO

proxy_enabled = 1
proxy_host = 'your.proxy.com'
proxy_port = 8123
list_count = 7

phonenum = '13800000000'

def print_log(loglevel, message):
    if loglevel >= log_level:
        print "[{}][{}] {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), loglevel, message)

def sleep_random(min, max):
    sec = random.randint(min,max)
    if DEBUG:
        print_log(DEBUG, "Sleeping {}s...".format(format(sec)))
    sleep(sec)

def get_tunnel_pids(host, port):
    try:
        pids = subprocess.check_output(['pgrep', '-f', 'ssh.*'+str(port)+'.*'+host]).rstrip("\n").split("\n")
        return pids
    except subprocess.CalledProcessError as e:
        return []

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
            return pids[0]
        else:
            raise RuntimeError, 'multiple (or zero?) tunnel ssh processes found: ' + str(pids) 
    else:
        raise RuntimeError, 'Error creating tunnel: ' + str(p) + ' :: ' + str(ssh_process.stdout.readlines())

def login(cj, phonenum):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = fix_headers

    # POST login
    formdata = { "version" : 'iPhone6-10.0.1', "versionNum": '2.3.0', "password" : '2eb897b5cacf49e65bc9b6a89bed89b8', "username" : phonenum }
    data_encoded = urllib.urlencode(formdata)
    req = urllib2.Request('http://api.kongkonghu.com/login', data_encoded, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'})
    try:
        responseobj = json.load(opener.open(req))
        if responseobj['code'] == 'success':
            print_log(INFO, "Logged into {}, seller_id {}".format(responseobj['userName'], responseobj['userId']))
            print_log(DEBUG, responseobj)
            return responseobj['userId']
        else:
            print_log(INFO, "Failed to log into {}".format(phonenum))
    except RuntimeError as e:
        print_log(ERROR, e.message)

def get_balance(cj):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = fix_headers

    req = urllib2.Request('http://api.kongkonghu.com/auth/user/balance')
    sleep_random(2,7)
    try:
        responseobj = json.load(opener.open(req))
        if responseobj['code'] == 'success':
            val = float(responseobj['available'])
            print_log(INFO, "Availiable balance is {}".format(val))
            print_log(DEBUG, responseobj)
            return val
        else:
            print_log(INFO, "Failed to get availiable balance.")
            return 0
    except RuntimeError as e:
        print_log(ERROR, e.message)

def withdraw_balance(cj, amount):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = fix_headers

    req = urllib2.Request('http://api.kongkonghu.com/auth/user/isbindalipay')
    sleep_random(2,7)
    try:
        responseobj = json.load(opener.open(req))
        if responseobj['errCode'] == 'already_bind':
            print_log(INFO, "Withdrawing the availiable balance to {}".format(responseobj['alipay']))
            print_log(DEBUG, responseobj)
        else:
            print_log(INFO, "Failed to get alipay account.")
    except RuntimeError as e:
        print_log(ERROR, e.message)

    formdata = { "withDraw" : amount}
    data_encoded = urllib.urlencode(formdata)
    req = urllib2.Request('http://api.kongkonghu.com/auth/money/withdraw', data_encoded, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'})
    sleep_random(2,7)
    try:
        responseobj = json.load(opener.open(req))
        if responseobj['errCode'] == '':
            print_log(INFO, "Withdraw amount {}".format(amount))
            print_log(DEBUG, responseobj)
        else:
            print_log(INFO, "Failed to withdraw the balance.")
    except RuntimeError as e:
        print_log(ERROR, e.message)

def get_list_count(cj, seller_id):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = fix_headers

    formdata = { "pageNum" : 1, "sellerId" : seller_id}
    data_encoded = urllib.urlencode(formdata)
    req = urllib2.Request('http://api.kongkonghu.com/products/selling', data_encoded, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'})
    sleep_random(2,7)
    try:
        responseobj = json.load(opener.open(req))
        if responseobj['code'] == 'success':
            selling_count = len(responseobj['list'])
            print_log(INFO, "Found {} items on selling list.".format(selling_count))
            print_log(DEBUG, responseobj)
            return selling_count
        else:
            print_log(INFO, "Failed to get list items.")
            return -1
    except RuntimeError as e:
        print_log(ERROR, e.message)

def list_item(cj, title, price, picfile, count):
    upload_opener = register_openers()
    upload_opener.add_handler(urllib2.HTTPCookieProcessor(cj))
    upload_opener.addheaders = fix_headers
    params = {'categoryId': '148', 'originalPrice': '0', 'currentPrice': price, 'description': title, 'brand': 'amazon', 'size': '', 'productName': 'amazon - '+title, 'condition': '1', 'releaseStatus': '0', 'productImages': open(picfile, "rb"), }

    datagen, headers = multipart_encode(params)
    request = urllib2.Request("http://api.kongkonghu.com/auth/product/add", datagen, headers)

    while count > 0:
        sleep_random(2,7)
        try:
            responseobj = json.load(upload_opener.open(request))
            if responseobj['code'] == 'success':
                print_log(INFO, "Listed new item, id = {}.".format(responseobj['product']['productId']))
                print_log(DEBUG, responseobj)
                count = count - 1
            else:
                print_log(INFO, "Failed to list new item.")
        except RuntimeError as e:
            print_log(ERROR, e.message)

fix_headers = [('User-agent', '空空狐 2.3.0 rv:183 (iPhone; iOS 10.0.1; zh_CN)'), ('Version', '2.3.0'), ('Os', 'iOS'), ('Accept-Encoding', 'gzip')]
cj = CookieJar()

try:
    if proxy_enabled:
        pids = get_tunnel_pids(proxy_host, proxy_port)
        if len(pids):
            print_log(INFO, "Using exsiting SSH tunnel to {} on local port {}, PID: {}".format(proxy_host, proxy_port, pids))
            pid = pids[0]
        else:
            pid = create_tunnel(proxy_host, proxy_port)
            print_log(INFO, "Creating SSH tunnel to {} on local port {}, PID: {}".format(proxy_host, proxy_port, pid))
        socks.set_default_proxy(socks.SOCKS5, "localhost", proxy_port)
        socket.socket = socks.socksocket

    seller_id = login(cj, phonenum)

    if seller_id:
        balance = get_balance(cj)
        if balance > 0:
            withdraw_balance(cj, balance)
        selling_count = get_list_count(cj, seller_id)
        if selling_count > 0 and selling_count < list_count:
            count = list_count - selling_count
            price = '320'
            title = 'amazon $50充值'
            picfile = "item.jpg"

            list_item(cj, title, price, picfile, count)

    if proxy_enabled:
        print_log(INFO, "Closing SSH tunnel to {} on local port {}, PID: {}".format(proxy_host, proxy_port, pid))
        os.kill(int(pid), signal.SIGTERM)

except RuntimeError as e:
    if proxy_enabled:
        print_log(INFO, "Closing SSH tunnel to {} on local port {}, PID: {}".format(proxy_host, proxy_port, pid))
        os.kill(int(pid), signal.SIGTERM)
    print_log(ERROR, e.message)

