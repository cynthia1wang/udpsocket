#coding:gbk
'''
Created on 2017年8月7日
@author: cynthia
''' 
__author__ = 'wangyan' 

from socket import socket, AF_INET, SOCK_DGRAM
import struct
import binascii
import functools
import types
import os
from functools import reduce


class SomeCustomError(Exception):
    def __init__(self,message):
        super(SomeCustomError,self).__init__()
        self.message = message

#定义装饰器
def send_session_start():
    def decorator(func):
        def wrapper(self,*args, **kw):
            print("send session start")
            self.serial_number = 1
            #拼接报文
            #消息ID（2B） 流水号（2B） 消息长度(2B)  消息内容（b'session_start'）
            format= "!H H H %ds" % len(b'session start')
            data = struct.pack(format,0x8E00,self.serial_number,len(b'session start'),b'session start')
            self.send_packet(data)
            #设置接收超时为1s
            self.sock.settimeout(1)
            #接收报文
            data = self.recv_packet()
            #检验消息ID是否合法
            msg_id = struct.unpack("!H",data[0:2])[0]
            if msg_id != 0x8E01:
                raise SomeCustomError('when send session start, msg_id is error')
            return func(self)
        return wrapper
    return decorator

def send_session_end():
    def decorator(func):
        def wrapper(self,*args, **kw):
            msg = func(self)
            print("send session end")
            #消息ID（2） 流水号（2B） 消息长度(2B)  消息内容（'session end'）
            format = "!H H H %ds" % len(b'session end')
            data = struct.pack(format,0x8E0A,self.serial_number,len(b'session end'),b'session end')
            #发送消息
            self.send_packet(data)
            #设置接收超时为1s
            self.sock.settimeout(1)
            data = self.recv_packet()
            msg_id = struct.unpack('!H',data[0:2])[0]
            if msg_id != 0x8E0B:
                raise SomeCustomError('when send session end, msg_id is error')
            return msg
        return wrapper
    return decorator

class MySock(object):
    __slots__ = ('__serial_number','sock','__serverIp','__serverPort')
    def __init__(self,serverIp,serverPort):
        self.__serial_number = 1
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.__serverIp = serverIp
        self.__serverPort = serverPort
    def __str__(self):
        return 'MySock object (serial_number:%d,serverIp:%s,serverPort:%d)' % (self.__serial_number,self.__serverIp,self.__serverPort)
    __repr__ = __str__
    @property
    def serial_number(self):
        return self.__serial_number
    @serial_number.setter
    def serial_number(self,value):
        self.__serial_number = value
       
    #发送消息，0x7e msg ehecksum 0x7e  
    #eg:0x7e 消息ID（2） 流水号（2B） 消息长度(2B)  消息内容（变长） 校验码（2B）0x7e
    def send_packet(self,data):
        #拼接消息头 0x7e
        format = 'B %ds B' % len(data)
        packet = struct.pack(format,0x7E,data,0x7E)
        self.sock.sendto(packet, (self.__serverIp,self.__serverPort))
        #更新流水号
        self.serial_number = self.serial_number + 1    

    #收包0x7e 消息ID（2） 流水号（2B） 消息长度(2B)  消息内容（变长） 0x7e
    def recv_packet(self):
        data,addr = self.sock.recvfrom(2048) 
        #打印收到的消息
        print ('recv = ',binascii.hexlify(data))
        #更新流水号
        pack_index = struct.unpack("!H",data[3:5])[0]
        if pack_index + 1 > self.serial_number:
            self.serial_number = pack_index + 1
        return data[1:len(data) - 1]

    #监测服务器状态
    @send_session_start()
    @send_session_end()  
    def send_heartbeat(self):
        print("send heart beat")
        #消息ID（2） 流水号（2B） 消息长度(2B)  消息内容（1）
        format = "!H H H %ds" % len(b'heart beat')
        data = struct.pack(format,0x8E08,self.serial_number,len(b'heart beat'),b'heart beat')
        self.send_packet(data)
        data = self.recv_packet()
        msg_id = struct.unpack('!H',data[0:2])[0]
        if msg_id != 0x8E09:
            raise SomeCustomError('when send heart beat, msg_id is error')
    
    def close(self):
        self.sock.close()
        
if __name__ == '__main__': 
    sock = MySock('127.0.0.1',20000)
    try:
        sock.send_heartbeat()
    except IOError:
        print("sock timeout")
    except SomeCustomError as x:
        print(x.message)
    sock.close()