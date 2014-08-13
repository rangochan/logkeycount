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
import functools
import copy
import os

copy_lock = threading.Lock()
def getip(ifname):
    socket_ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(socket_ip.fileno(), 0x8915, \
            struct.pack('256s', ifname[:15]))[20:24])

def sender(tmpdict):
    global thread_t
    thread_t = threading.Timer(time_interval, sender)
    thread_t.start()

    if copy_lock.acquire(1):
        dict_n = copy.deepcopy(tmpdict)
        for i in tmpdict:
            tmpdict[i] = 0
        copy_lock.release()

    ip_addr = getip("eth0")
    # write count results into local file
    try:
        fileopen = open("/usr/home/shixi_jiangen/results.out", 'w')
    except Exception as err:
        sys.stderr.write("Error to make a file to write with results: \
                %s\n" % err)
        return err

    for i in dict_n:
        count = str(dict_n[i])
        element = ip_addr + ' ' + i + ' ' + count + '\n'
        fileopen.write(element)
    fileopen.close()

    # system call zabbix_sender to send data
    subprocess.call('zabbix_sender -i results.out -z 127.0.0.1 -vv', \
            shell=True)

def get_list(config_file):
    # read configuration file
    conf = ConfigParser.ConfigParser()
    conf.read(config_file)

    # get configuration details and store into a list
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
    # init a dict used to store results
    tmpdict = {}
    for i in range(len(tmplist)):
        inf = tmplist[i][0] + '_' + tmplist[i][1]
        tmpdict[inf] = 0
    return tmpdict

if __name__ == '__main__':
    # get count interval
    conf = ConfigParser.ConfigParser()
    conf.read("/usr/home/shixi_jiangen/logconf.ini")

    time_interval = conf.getint("main", "time_interval")
    regex = conf.get("template", "re")

    tmplist = get_list("/usr/home/shixi_jiangen/logconf.ini")
    tmpdict = get_dict(tmplist)

    sender = functools.partial(sender, tmpdict)
    thread_t = threading.Timer(time_interval, sender)
    thread_t.start()

    while 1:
        line = sys.stdin.readline()
        if not line:
            os._exit(0)

        re_match = re.match(regex, line)
        if re_match is None:
            sys.stderr.write("Unable to parse log message - " + \
                    "\n%s\n" % line)
            continue

        for tmptuple in tmplist:
            pp = tmptuple[0] + '_' + tmptuple[1]
            if re_match.group(1) == tmptuple[0]:
                if (re_match.group(2)).find(tmptuple[1]) >= 0:
                    tmpdict[pp] += 1
