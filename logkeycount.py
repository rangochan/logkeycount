#!/usr/bin/env python
# coding=utf-8
"""Description: count the number of the specified key word present
in every line of log message from rsyslog, then send statistics
results to zabbix server via calling zabbix_sender command line tool
"""

import sys
import ConfigParser
import re
import threading
import socket
import fcntl
import struct
import subprocess
import copy
import os
import time

RESULTS_FILE = '/var/results.out'
CONFIG_FILE = '/etc/logconf.ini'
tmpdict = {}
tmplist = []

def getip(ifname):
    '''get local ip address depending on the specified interface'''
    socket_ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(socket_ip.fileno(), 0x8915, \
            struct.pack('256s', ifname[:15]))[20:24])

def sender(tmpdict, time_interval):
    '''send results to zabbix server every time_interval seconds'''
    while True:
        time.sleep(time_interval)
        dict_n = copy.deepcopy(tmpdict)
        for i in tmpdict:
            tmpdict[i] = 0
        write_file(dict_n)

        # system call zabbix_sender to send data
        subprocess.call(zabbix_cmd, shell=True)

def get_list():
    '''get configuration details and store into a list'''
    global conf
    tmplist = []
    sections = conf.sections()
    for section in sections:
        if section == "main" or section == "template":
            continue
        else:
            options = conf.options(section)
            for option in options:
                key = conf.get(section, option)
                keywd = section, key
                tmplist.append(keywd)
    return tmplist

def get_dict(tmplist):
    '''init a dict used to store results'''
    tmpdict = {}
    for i in range(len(tmplist)):
        inf = tmplist[i][0] + '_' + tmplist[i][1]
        tmpdict[inf] = 0
    return tmpdict

def count_key(line):
    re_match = re.match(regex, line)
    if re_match is None:
        sys.stderr.write("Unable to parse log message: " + \
                "\n%s\n" % line)
        return
    
    global tmplist
    global tmpdict
    for tmptuple in tmplist:
        pp = tmptuple[0] + '_' + tmptuple[1]
        if re_match.group(1) == tmptuple[0]:
            if (re_match.group(2)).find(tmptuple[1]) >= 0:
                tmpdict[pp] += 1

def write_file(tmpdict):
    '''write count results into local file'''
    try:
        fileopen = open(RESULTS_FILE, 'w')
    except Exception as err:
        sys.stderr.write("Error to make a file to write with results: \
                %s\n" % err)

    for i in tmpdict:
        count = str(tmpdict[i])
        element = IP_ADDR + ' ' + i + ' ' + count + '\n'
        fileopen.write(element)
    fileopen.close()

conf = ConfigParser.ConfigParser()
conf.read(CONFIG_FILE)

time_interval = conf.getint("main", "time_interval")
regex = conf.get("template", "re")
zabbix_cmd = conf.get("main", "zabbix_sender")
ifname = conf.get("main", "ifname")
debug = conf.get("main", "debug")
test_file = conf.get("main", "test_log")

tmplist = get_list()
tmpdict = get_dict(tmplist)
IP_ADDR = getip(ifname)

file = conf.get("main", "results_file")
if file:
    RESULTS_FILE = file

# if debug is true, execute the test, otherwise execute as normal
if debug == 'True' or debug == 'true':
    fh = open(test_file, 'rb')
    data = fh.readlines()
    for line in data:
        count_key(line)
    write_file(tmpdict)
    subprocess.call(zabbix_cmd, shell=True)
else:
    t = threading.Thread(target=sender(tmpdict, time_interval))
    t.start()
    while 1:
        line = sys.stdin.readline()
        if not line:
            subprocess.call(zabbix_cmd, shell=True)
            os._exit(0)
        count_key(line)
