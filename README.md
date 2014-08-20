logkeycount
===========

a small tool to count the number of the specified keyword present in log message from rsyslog, then send results to zabbix server

howto
===========
1. put the configuration file:logconf.ini into /etc

2. configure logkeycount.py: 
  1. set the regex expression at the section "template" depending on your log message format
  2. set the keyword and subkeyword as keywords which are going to be mathed depending your requirment
  3. set debug: true for test, false or others for execution as normal

3. configure rsyslog
configure rsyslog omprog setction according to your situation

4. restart rsyslog
'''
service rsyslog restart
'''
