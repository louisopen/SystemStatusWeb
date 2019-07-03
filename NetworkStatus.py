#!/usr/bin/env python
#coding:utf-8 
#You may need pip install psutil
import time

try:
    import psutil
except ImportError:
    print('Error: psutil module not found!')
    exit()

def get_key():
    key_info = psutil.net_io_counters(pernic=True).keys()  # 網路介面訊息區域網路,bluebooth,WiFi
    recv = {}
    sent = {}
    #recv.setdefault(key, psutil.net_io_counters(pernic=False).bytes_recv)   #總接收數
    #sent.setdefault(key, psutil.net_io_counters(pernic=False).bytes_sent)   #總發射數
    for key in key_info:
        recv.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_recv)  # 各网卡接收的字节数
        sent.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_sent)  # 各网卡发送的字节数
    return key_info, recv, sent

    #net = psutil.net_io_counters() # 目前網路連線訊息(可能很多)
    #print(net)
    #net = psutil.net_connections() # 目前網路連線訊息(可能很多)
    #print(net)

def get_rate(func):     
    key_info, old_recv, old_sent = func()  # 上一秒收集的数据
    time.sleep(1) 
    key_info, now_recv, now_sent = func()  # 当前所收集的数据
    net_in = {}
    net_out = {}
 
    for key in key_info:
        net_in.setdefault(key, (now_recv.get(key) - old_recv.get(key)) / 1024 / 1024)  # 每秒接收速率MB
        net_out.setdefault(key, (now_sent.get(key) - old_sent.get(key)) / 1024 / 1024) # 每秒发送速率MB
    
    #old_recv = now_recv
    #old_sent = now_sent
    return key_info, net_in, net_out
 



while True:
    try:
        ip_file = open('networkstatus.txt','a')
        ip_file.write(time.strftime("[%Y-%m-%d %H:%M:%S]")+'\n')
  
        key_info, net_in, net_out = get_rate(get_key) 
        for key in key_info:           # 各網路介面(區域網路,bluebooth,WiFi,vEthernet)
            msg='''Interface = {}\nReceived = {}MB/s\nTransmit = {}MB/s\n'''.format( key, net_in.get(key), net_out.get(key))
            ip_file.write(msg)
            #print("TIME = " + time.strftime("%Y-%m-%d %H:%M:%S "))
            #print('%s\nInput:\t %-5sKB/s\nOutput:\t %-5sKB/s\n' % (key, net_in.get(key), net_out.get(key)))
         
        from os.path import basename
        from psutil import net_connections,Process
        for x in net_connections('all'):
            laddr, raddr, status, pid=x[3:]
            if not raddr:
                continue
            try:
                filename = basename(Process(pid).exe()) #專注於exe程序
            except:
                pass
            else:
                msg='''Process = {} Local = {} Remote = {} Connection = {}\n'''.format(filename, laddr, raddr, status)
                #print(msg)
                ip_file.write(msg)

        ip_file.write('\n')
        ip_file.close() 
    except KeyboardInterrupt:
        exit()